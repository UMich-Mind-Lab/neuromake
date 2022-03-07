"""utility functions"""

import os
import re
import json
import nibabel as nib
import itertools as it
import neuromake as nm
import neuromake.exceptions as err

keynames = os.path.join(os.path.dirname(__file__),
                        'config','keynames.json')
with open(keynames,'r') as fp:
    _bidsKeyNames = json.load(fp)

def multireplace(s,rep,match_end=False):
    '''
    return string 's' after simultaneous replacement of all possible rep keys()
    with rep values()

    :param s: original string
    :param rep: dictionary where keys are substrings, and values are replacements
    :param match_end: only replace substrings that match the end of string s
    :return: replaced string
    '''
    new = {}
    kesc = [ re.escape(k) for k in rep.keys() ]
    if match_end:
        pattern = re.compile('$|'.join(kesc)+'$')
    else:
        pattern = re.compile('|'.join(kesc))
    return pattern.sub(lambda m: rep[m.group(0)],s)

def multireplace_dict_keys(d,rep,match_end=False):
    '''
    return dict 'd' after simultaneous replacement of all possible 'rep' keys()
    with 'rep' values()

    :param d: dict to modify
    :param rep: dict where keys are substrings, values are replacements
    :param match_end: only replace substrings that match the end of any key in 'd'
    :return: replaced dict
    '''
    new = {}
    for k in d.keys():
        new[multireplace(k,rep)] = d[k]
    return new

def get_n_combos_per_sub(d):
    '''
    calculates combinations of bids vars per subject in the specified dictionary
    this is used to calculate number of expected files when validating subjects
    '''
    d.pop('subject',None)
    vals = []
    for k,v in d.items():
        if isinstance(v,list):
            vals.append(v)
        else:
            vals.append([v])
    combinations = it.product(*vals)
    return len(list(combinations))

def get_bids_vars_dict(bidsfile,add_prefix=True):
    '''
    function reads a bids filename and returns key-value pairs in a dictionary.
    If add_prefix is True, then each key is prefixed with <filetype>_, such that
    the output dictionary matches variables supplied in config['bids'].

    :bidsfile: filepath of BIDS formatted file
    :add_prefix: boolean to specify if keys should be prefixed with <filetype>_
    :return: dictionary with bids key-value pairs
    '''
    config = nm.Config()
    b = re.split('-|_',os.path.basename(bidsfile))
    # add suffix/extension
    b.insert(-1,'suffix')
    b[-1],ext = b[-1].split('.',1)
    d = { b[i]:b[i+1] for i in range(0,len(b),2) }
    d['extension'] = ext
    # replace labels with variable names
    label2key = { v:k for k,v in config._bidsKeyNames.items() }
    d = multireplace_dict_keys(d,label2key,match_end=True)

    # get the filetype based on bids suffix
    filetype = config.get_bids_filetype(bidsfile)
    dout = {}
    for k,v in d.items():
        if k in config._bidsFileTypes[filetype]['labels']:
            if add_prefix:
                dout[filetype+'_'+k] = v
            else:
                dout[k] = v
        else:
            dout[k] = v
    return dout

def query_bids_layout(layout,d,ext=['nii.gz','nii']):
    '''
    queries the bids layout given available wildcards dictionary
    returns output from layout.get()
    '''
    rep = {'func_':'','anat_':'','physio_':'','fmap_':''}
    d = multireplace_dict_keys(d,rep)
    d['extension'] = ext
    return layout.get(**d)

def copy_bids_files(wildcards,layout,output,ext=['nii.gz','nii']):
    '''
    format snakemake wildcards as dictionary, search through BIDSLayout to
    find appropriate mri file + associated json.
    The associated snakemake rule must have a "nii" and "json" object
    '''
    # create dictionary from wildcards, get extension from output
    d = vars(wildcards)
    d.pop('_names',None)
    d['extension'] = ext
    files = query_bids_layout(d,layout)
    if not(len(files) == 1):
        raise Exception(f'{len(files)} files found when 1 expected. This usually means your bids variables in Config do not match those expected in the dataset')
    else:
        nib.save(files[0].get_image(),output.nii)
        with open(output.json,'w+') as fp:
            json.dump(d, fp)
        save_dict_to_json(files[0].get_metadata(),output.json)
