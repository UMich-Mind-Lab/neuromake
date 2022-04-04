"""sample Apps to use as base class"""

from .app import App
from ..wildcard import Wildcard, PathWildcard, TemplateWildcard
from ..menu import Menu
import importlib.resources
import json

def get_sample_app(name="default"):
    """return a sample neuromake App"""
    pass

def _minimal_app(file_type='func'):
    """
    the default app includes:

    - bids Menu: minimally required wildcards only (matching specified filetype)
    - templates Menu: a prefix for each filetype included
    - directory Menu: output, working, bids, bidslayout
    - params Menu: an empty params Menu
    """
    bids_info = _get_bids_info()
    if file_type not in bids_info.keys():
        raise ValueError(f'"{file_type}" must be one of {list(bids_info.keys())}.')

    wildcards = []



def _make_bids_menu():
    """create a bids menu object with appropriate metadata"""



def _get_bids_info():
    with importlib.resources.open_text('neuromake.resources','bids_info.json') as file:
        file_types = json.load(file)
    return file_types
