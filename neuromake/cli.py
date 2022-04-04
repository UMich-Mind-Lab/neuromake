#!/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import os
import sys
import argparse,argcomplete
import json
from neuromake.app import App
from neuromake.menu import Menu
from neuromake.wildcard import Wildcard

def _get_property_setter(obj,property_name):
    property = getattr(obj,property_name)
    return property.fset

_APP_METHOD_MAP = {
    'set_name': {
        'func': _get_property_setter(App,'name'),
        'nargs':1,
        'metavar':('app_name')
    },
    'set_cfg': {
        'func': _get_property_setter(App,'cfg_path'),
        'nargs':1,
        'metavar':('cfg_path')
    },
    'set_sm_cfg': {
        'func': _get_property_setter(App,'sm_cfg_path'),
        'nargs':1,
        'metavar':('sm_cfg_path')
    },
    'add_menu': {
        'func': lambda m,x: m.add_menu(Menu(name=x)),
        'nargs':1,
        'metavar':('menu_label')
    },
    'remove_menu': {
        'func': lambda m,x: m.remove_menu(x),
        'nargs': 1,
        'metavar': ('menu_label')
    }
}
_MENU_METHOD_MAP = {
    'set_name': {
        'func': _get_property_setter(Menu,'name'),
        'nargs': 1,
        'metavar': ('menu_name')
    },
    'set_metadata': {
        'func': lambda m,k,v: m.set_metadata(**{k,v}),
        'nargs': 2,
        'metavar': ('label','key')
    },
    'add_wildcard': {
        'func': lambda m,x: m.add_wildcard(Wildcard(label=x)),
        'nargs': 1,
        'metavar': ('wildcard_label')
    },
    'remove_wildcard': {
        'func': lambda m,x: m.remove_wildcard(x),
        'nargs': 1,
        'metavar': ('wildcard_label')
    },
    'reset': {
        'func': lambda m: m.reset(),
        'nargs': 0,
        'metavar': None
    },
    'factory_reset': {
        'func': lambda m: m.factory_reset(),
        'nargs': 0,
        'metavar': None
    }
}
_WILDCARD_METHOD_MAP = {
    'set_metadata': {
        'func': lambda w,k,v: w.set_metadata(**{k,v}),
        'nargs': 2,
        'metavar': ('label','key')
    },
    'set_label': {
        'func': _get_property_setter(Wildcard,'label'),
        'nargs': 1,
        'metavar': ('label')
    },
    'set_value': {
        'func': _get_property_setter(Wildcard,'value'),
        'nargs': '?',
        'metavar': ('value')
    },

}


def cli():
    '''
    Command-line interface for Neuromake.
    '''
    # first argparse pass -- check if there's a config file specified, the
    # rest of the options depend on it.
    early_args,remainder_argv = _early_parser()

    app = App(cfg_path=early_args.config)
    if early_args.no_display:
        args = _parse_args(app,remainder_argv)
    #else:
    #   gui(config)

def _early_parser():
    '''
    Specify options for initializing neuromake.
    '''
    early_parser = argparse.ArgumentParser(description=__doc__,add_help=False)

    early_parser.add_argument('-c','--config',default='neuromake.cfg',help='neuromake config filepath.')
    early_parser.add_argument('-n','--new',action='store_true',default=False,help='create new neuromake config file.')
    early_parser.add_argument('--no-display',action='store_true',default=False,help='make changes to neuromake.cfg through the command-line interface.')

    args,remainder_argv = early_parser.parse_known_args()

    return args,remainder_argv


def _generate_method_map_parsers(subparsers,method_map,obj=None,parentobj=None):
    '''
    create all subparsers from method_map

    subparsers: output of ArgumentParser.add_subparsers
    method_map: method_map (globals)
    obj: object instance to grab methods from in lambda functions

    '''
    for k,v in method_map.items():
        method_parser = subparsers.add_parser(k,description=v['func'].__doc__)
        method_parser.set_defaults(func=v['func'])
        if isinstance(v['nargs'],str):
            method_parser.add_argument(f'arg{x}',nargs=v['nargs'],metavar=v['metavar'])
        elif isinstance(v['nargs'],int):
            for x in range(0,v['nargs']):
                method_parser.add_argument(f'arg{x}',metavar=v['metavar'][x])
                if obj is not None:
                    method_parser.add_argument('--obj',action="store_const",const=obj,default=obj,help=argparse.SUPPRESS)
                elif parentobj is not None:
                    method_parser.add_argument('--parentobj',action="store_const",const=parentobj,default=parentobj,help=argparse.SUPPRESS)

def _parse_args(app,argv):
    '''
    Neuromake is a helper tool designed to help snakemake pipelines work more
    seamlessly with the dynamic nature of bids variables
    '''
    global _APP_METHOD_MAP
    global _MENU_METHOD_MAP
    global _WILDCARD_METHOD_MAP

    ap = argparse.ArgumentParser(description=__doc__)

    app_subparsers = ap.add_subparsers(help='App methods')
    _generate_method_map_parsers(app_subparsers,_APP_METHOD_MAP,app)

    menus_parser = app_subparsers.add_parser('menu',description='Neuromake Menu Options')
    menus_subparsers = menus_parser.add_subparsers(help='specify menu',dest='menu')

    for menu in app._menus:
        menu_parser = menus_subparsers.add_parser(menu.name,description=menu.__doc__)
        menu_subparsers = menu_parser.add_subparsers()
        _generate_method_map_parsers(menu_subparsers,_MENU_METHOD_MAP,menu)
        # now wilcard loop
        wildcards_parser = menu_subparsers.add_parser('wildcard',description='Neuromake Wildcard Options')
        wildcards_subparsers = wildcards_parser.add_subparsers(help='specify wildcard')
        for wildcard in menu._wildcards:
            wildcard_parser = wildcards_subparsers.add_parser(wildcard.label,description=wildcard.__doc__)
            wildcard_subparsers = wildcard_parser.add_subparsers()
            _generate_method_map_parsers(wildcard_subparsers,_WILDCARD_METHOD_MAP,wildcard)

    args = vars(ap.parse_args(argv))
    func = args.pop('func')
    obj = args.pop('obj')

    #func(obj,*args.values())
    #print(json.dumps(obj.to_dict(),indent=2))

    return




    # app methods
    ap.add_argument('--set-name',type=str,)
    menu_subparsers = ap.add_subparsers(help='neuromake config menus')
    for menu in app._menus:

        menu_subparser = menu_subparsers.add_parser(menu.name)
        wildcard_subparsers = menu_subparser.add_subparsers(help=f'Wildcards in {menu.name}.')
        for wildcard in menu._wildcards:
            _WILDCARD_METHOD_MAP = {
                'set_label': lambda x: wildcard.label.__setter__(x)
            }
            print(wildcard.label,wildcard.value)

    args = ap.parse_args(argv)

    print(args)
    return args
#
#
#
#
#     parser = argparse.ArgumentParser()
# subparsers = parser.add_subparsers(help='types of A')
# parser.add_argument("-v", ...)
#
# a_parser = subparsers.add_parser("A")
# b_parser = subparsers.add_parser("B")
#
# a_parser.add_argument("something", choices=['a1', 'a2'])
#
#
#     ap.add_argument('menu',choices=[x.label for x in app._menus],help='neuromake menu labels')
#     ap.add_argument(''
#         '--reindex',
#         action="store_true",
#         help='reindex SQL database for BIDSLayout if bids_layout_db specified in snakemake config file [default: false]'
#     )
#     ap.add_argument(
#         '--make-default-templates',
#         action="store_true",
#         help='based on current BIDS variables, construct default snakemake templates [default: false]'
#     )
#     ap.add_argument(
#         '--get-valid-subjects',
#         action="store_true",
#         help='based on current BIDS variables, update subjects to all those that have all expected BIDS files. [default: false]'
#     )
#     ap.add_argument(
#         '--dry-run',
#         action='store_true',
#         help='Do not execute anything, and display what would be done. [default: false]'
#     )
#     ap.add_argument(
#         '-v','--verbosity',
#         action='store_true',
#         help='set verbose output [default: false]'
#     )
#
#     # for each menu dictionary, users have the option to add a new wildcard,
#     # remove a wildcard, set the values for a wildcard, or set a wildcard as required/not
#     subparsers = ap.add_subparsers(dest='menu',help='specify menus menu')
#     for k,v in config.config.items():
#         current_parser = subparsers.add_parser(k,help=v['__metadata__']['help'])
#         current_parser.add_argument('action',choices=['add','set','set-optional','set-required','remove'],help=f'specify action to perform within {k} menu')
#         current_parser.add_argument('label',help='wildcard label')
#         current_parser.add_argument('value',nargs='*',default=[],help='set wildcard value(s)')
#
#     argcomplete.autocomplete(ap)
#     if args is None:
#         args = vars(ap.parse_args())
#     else:
#         args = vars(ap.parse_args(args))
#     return args

if __name__ == '__main__':
    cli()
