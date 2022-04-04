"""sample Menu objects to build App"""

from .menu import Menu
from ..wildcard import Wildcard, PathWildcard, TemplateWildcard
import importlib.resources
import json

__ALL__ = ['create_bids_menu']

with importlib.resources.open_text('neuromake.resources','bids_info.json') as x:
    _BIDS_INFO = json.load(x)

def create_bids_menu(filetype,level='minimal'):
    '''
    make a sample bids menu.

    - filetype (str or list of str): "bids file type(s) to include"
    - level (str): "minimal" or "all" [default: "minimal"]
    '''
    global _BIDS_INFO

    DEFAULT_METADATA = {
        'var_type':'str',
        'iterable':True,
    }
    MENU_HELP_TXT = (
        "menu containing wildcard variables pertaining to the BIDS. These"
        "wildcards are used to find the input files for the"
        "snakemake workflow (via PyBIDS), meaning all relevant BIDS variables"
        "present in your specific dataset should be specified here. Note that"
        "keywords that correspond to more than one bids file type/modality"
        "(e.g., acquisition) are given a prefix to make them unique."
    )

    valid_menu_labels = []
    for k,v in _BIDS_INFO.items():
        prefix = ''
        if k != 'base':
            prefix = f'{k}_'
        x = [ f'{prefix}{label}' for label in v['labels']['all']]
        valid_menu_labels.extend(x)

    if isinstance(filetype,str):
        filetype = [filetype]
    if not(isinstance(filetype,list)):
        msg = f'filetype must be type list, not "{type(filetype).__name__}".'
        raise TypeError(msg)
    if 'base' not in filetype:
        filetype.insert(0,'base')

    wildcards = []
    for x in filetype:
        if x == 'base':
            prefix=''
        else:
            prefix=f'{x}_'
        if x not in _BIDS_INFO.keys():
            msg = (
            f'"{x}" is not a recognized file type. Must be one of '
            f'{list(_BIDS_INFO.keys())}.'
            )
            raise ValueError(msg)
        if level not in _BIDS_INFO[x]['labels'].keys():
            msg = (
                f'"{x}" does not have level "{level}".'
                f'Must be one of {list(_BIDS_INFO[x].keys())}.'
            )
            raise ValueError(msg)
        for label in _BIDS_INFO[x]['labels'][level]:
            metadata = DEFAULT_METADATA.copy()
            if label in _BIDS_INFO[x]['labels']['minimal']:
                metadata['required'] = True
            w = Wildcard(f'{prefix}{label}',None,metadata=metadata)
            wildcards.append(w)

    menu_metadata = {
        'help': MENU_HELP_TXT,
        'required':True,
        'valid_labels':valid_menu_labels
    }
    menu = Menu('bids',wildcard=wildcards,metadata=menu_metadata)
    return menu

def create_paths_menu():
    """
    make a sample path menu. By default, neuromake requires a "bids"
    path and a "bidslayout" path. Without these paths properly
    specified, PyBIDS will be unable to grab bids input files.

    It also requires "output" and "working" paths, to specify the base
    path for working files, and final output files.

    Other paths MAY be added, such as a path to an SPM installation, paths
    to packages, containers, additional config settings, you name it!
    """

    OUTPUT_HELP = (
    'Output path for neuromake application. This path should be specified '
    'by the user to indicate the base path for final output of the '
    'snakemake pipeline. Ideally, this path should be considered a BIDS '
    'derivatives base folder. This variable is accessible through '
    '`config["paths"]["output"]` within a corresponding snakefile.'
    )
    WORKING_HELP = (
    'Working path for neuromake application. This path should be specified '
    'by the user to indicate the base path for temporary working files. '
    'This variable is accessible through `config["paths"]["working"]` '
    'within a corresponding snakefile'
    )
    BIDS_HELP = (
    'Base path for BIDS dataset. PyBIDS uses this path to find the BIDS input '
    'required by the pipeline.'
    )
    BIDSLAYOUT_HELP = (
    'Base path for BIDSLayout sqlite database. PyBIDS offers functionality to '
    'speed up BIDS queries by constructing a database. Because snakemake will '
    'recursively make a non-trivial number of queries to the dataset, this '
    'database is required. If a path is specified that does not yet exist, '
    'the BIDSLayoutDB will be constructed before the first query at the target '
    'location.'
    )
    MENU_HELP_TXT = (
    'The `paths` menu is responsible for handling any static paths required by '
    'a snakemake workflow. By default, this menu includes the required '
    '"output", "working", "bids", and "bidslayout" paths.'
    '''Other common uses for the Paths menu include:
        - paths to software containers, libraries, or external scripts
        - paths to license files
        - paths to additional config files or settings files
    '''
    )
    w_output = PathWildcard(
        label='output',
        value=None,
        metadata={'help':OUTPUT_HELP}
    )
    w_working = PathWildcard(
        label='working',
        value=None,
        metadata={'help':WORKING_HELP}
    )
    w_bids = PathWildcard(
        label='bids',
        value=None,
        metadata={'help':BIDS_HELP}
    )
    w_bidslayout = PathWildcard(
        label='bidslayout',
        value=None,
        metadata={'help':BIDSLAYOUT_HELP}
    )
    wildcards = [w_output,w_working,w_bids,w_bidslayout]

    menu_metadata = {
        'help': MENU_HELP_TXT,
        'required':True,
        'wildcard_type':'PathWildcard'
    }
    menu = Menu('paths',wildcard=wildcards,metadata=menu_metadata)
    return menu
