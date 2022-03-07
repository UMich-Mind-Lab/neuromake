import os
import time
import json
import pandas as pd
import nibabel as nib
from string import Formatter
from bids import BIDSLayout

configfile: 'config/sm_config.json'

# pseudorule to specify snakemake final expected output. In this template example,
# the output is the fieldmap created via topup from dir-AP and dir-PA PEPolar
# fieldmaps
rule all:
    input:
        expand(f'{config["templates"]["anatDir"]}/eu{config["templates"]["anatPrefix"]}.nii.gz',**config['bids'])


################################################################################
#################### BIDS Variable Helper Functions ############################
################################################################################

def save_dict_to_json(d,out):
    '''
    function saves dictionary <d> to filename <out>
    '''
    with open(out,'w+') as fp:
        json.dump(d, fp)


def expand_some(s,d):
    '''
    In neuroimaging workflows, it is common to combine certain files in certain
    processing steps (e.g., tedana combines echos, a subject-level model that
    combines runs). This is done in snakemake via the expand function, which
    expands every variable in {}s to everything defined in kwargs (or **dict)

    However, we don't typically want to replace every variable, just the one we
    are putting together in that particular step. Snakemake handles this by
    allowing variables in {{}}s to not be expanded, but that's a little awkward
    when the wildcards are hosted inside a template string. So, this function
    does that for us:

    >>> d = {'run':['1','2','3']}
    >>> expand_some('sub-{sub}/ses-{ses}/run-{run}/bold.nii.gz',d)
    [ 'sub-{sub}/ses-{ses}/run-1/bold.nii.gz',
      'sub-{sub}/ses-{ses}/run-2/bold.nii.gz',
      'sub-{sub}/ses-{ses}/run-3/bold.nii.gz' ]

    :param filestr: filestring containing wildcards
    :d: dictionary with wildcards to expand
    :return: list of files with specified wildcards expanded
    '''
    fnames = set([ x for _,x,_,_ in Formatter().parse(filestr) ])
    for x in fnames:
        if x not in d.keys():
            d[x] = '{' + x + '}'
    return expand(filestr,**d)


################################################################################
####################### BIDS Raw to Working Rules ##############################
################################################################################
'''
These rules grab the BIDS files and move them to the generic template paths. If
you are using generic templates, then this section should not be altered.
Otherwise, you may need to update the formatting and logic to suit your needs.
Generic templates can be referred to in the following way.

anat -> {config['templates']['anatDir']}/{config['templates']['anatPrefix'].nii.gz}
func -> {config['templates']['funcDir']}/{config['templates']['funcPrefix'].nii.gz}
dwi -> {config['templates']['dwiDir']}/{config['templates']['dwiPrefix'].nii.gz}

If generic templates are not used, you'll need to update templates and some of
the logic used in the rules below

Not getting fieldmaps here because you may want to include further logic for
fieldmaps (i.e., pepolar fieldmaps turned into real fieldmaps via topup, prior
to assigning them to a specific functional image).
'''

if 'anatDir' in config['templates']:
    rule getBIDSAnat:
        output:
            nii = temp(f'{config["templates"]["anatDir"]}/{config["templates"]["anatPrefix"]}.nii.gz'),
            json = temp(f'{config["templates"]["anatDir"]}/{config["templates"]["anatPrefix"]}.json')
        run:
            copy_bids_files(wildcards,output)


if 'funcDir' in config['templates']:
    rule getBIDSFunc:
        output:
            nii = temp(f'{config["templates"]["funcDir"]}/{config["templates"]["funcPrefix"]}.nii.gz'),
            json = temp(f'{config["templates"]["funcDir"]}/{config["templates"]["funcPrefix"]}.json')
        run:
            layout = BIDSLayout(config['directories']['bids'],database_path=config['directories']['bidslayout'])
            func = query_bids_layout(wildcards,layout)
            if len(func) > 1:
                raise Exception(f'({len(func)}) files found when 1 expected. This usually means your bids variables do not match those expected in the dataset')
            else:
                nib.save(func[0].get_image(),output.nii)
                save_dict_to_json(func[0].get_metadata(),output.json)

if 'dwiDir' in config['templates']:
    rule getBIDSDwi:
        output:
            nii = temp(f'{config["templates"]["dwiDir"]}/{config["templates"]["dwiPrefix"]}.nii.gz'),
            json = temp(f'{config["templates"]["dwiDir"]}/{config["templates"]["dwiPrefix"]}.json')
        run:
            layout = BIDSLayout(config['directories']['bids'],database_path=config['directories']['bidslayout'])
            dwi = query_bids_layout(wildcards,layout)
            if len(dwi) > 1:
                raise Exception(f'({len(dwi)}) files found when 1 expected. This usually means your bids variables do not match those expected in the dataset')
            else:
                nib.save(dwi[0].get_image(),output.nii)
                save_dict_to_json(dwi[0].get_metadata(),output.json)


################################################################################
########################## PREPROCESSING RULES  ################################
################################################################################
'''
Here we specify preprocessing rules. Because we're using these template strings,
there's a couple things you might run into.

First, it's very common to "flatten" certain bids variables during processing --
you might combine echos via tedana, or combine runs into a subject level model.
In this case, the template may seem unintuitive. While expand (and expand_some),
can be used to collect the necessary input files, the output also needs to have
that wildcard removed. While a string replacement may work for individual rules
(e.g., f"{funcDir}".replace('{echo}','combined') ), this can get clunky and
unreadable over the course of a pipeline.

In this case, I'd recommend creating additional templates to account for the
combined directories (e.g., "tedanaDir", "subjectModelDir" ), and then reference
those

If it improves readability, abandon bids variables as wildcards and use arbitrary
ones (e.g., when the process is one-to-one, or in the same directory)

Snakemake is powerful and constantly evolving -- see the official documentation
for specific use cases, but below I provide a couple examples for how rules
can be put together
'''

# combining a wildcard into a new directory, using expand_some to expand only
# the 'func_echo' wildcard
# rule tedana:
#     input:
#         bold = expand_some(f'{config["templates"]["funcDir"]}/{config["templates"]["funcPrefix"]}.nii.gz',{'func_echo':config['bids']['func_echo']}),
#         json = expand_some(f'{config["templates"]["funcDir"]}/{config["templates"]["funcPrefix"]}.json',{'func_echo':config['bids']['func_echo']})
#     output:
#         cBold = f'{config["templates"]["funcDir"].replace("{echo}","comb")}/desc-optcomDenoised_bold.nii.gz'
#     params:
#         neurotools = config['containers']['neurotools']
#     shell:
#         '''
#         echos=""
#         for x in {input.json}; do
#             e=$(cat $x | jq '.EchoTime')
#             e=$(echo "$e * 1000" | bc )
#             echos="$echos $e"
#         done
#         singularity run -H $PWD {params.neurotools} tedana -d {input.bold} \
#             -e $echos --out-dir $(dirname {output.cBold})
#         '''

# using arbitrary wildcards for intermediary step
# notes that snakemake doesn't read nested config dictionary properly in shell
# commands, and so is instead specified as a parameter
rule unifize:
    input:
        '{filedir}/{fileprefix}_T1w.nii.gz'
    output:
        '{filedir}/u{fileprefix}_T1w.nii.gz'
    params:
        neurotools = config['containers']['neurotools']
    shell:
        'singularity run -H $PWD {params.neurotools} 3dUnifize -input {input} -prefix {output}'

# explicitly connect output of previous rule to new rule
rule bet:
    input:
        rules.unifize.output
    output:
        '{filedir}/eu{fileprefix}_T1w.nii.gz'
    params:
        neurotools = config['containers']['neurotools']
    shell:
        'singularity run -H $PWD {params.neurotools} bet2 {input} {output}'
