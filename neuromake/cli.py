# PYTHON_ARGCOMPLETE_OK
import os
import sys
import neuromake as nm
import argparse, argcomplete
import json

def cli():
    cfg_paths = [
        os.path.join(os.getcwd(),'neuromake.json'),
        os.path.join(os.getcwd(),'config','neuromake.json')
    ]
    cfg = ''
    while not(os.path.isfile(cfg)):
        try:
            cfg = cfg_paths[0]
            del cfg_paths[0]
        except:
            cfg = None
            break
    config = nm.Config(cfg)
    args = _parseargs(config)
    print(args)
    config.get_bids_layout(args['reindex'])
    if args['make_default_templates']:
        config.make_default_templates()
    if args['get_valid_subjects']:
        config.get_valid_subjects()


def _parseargs(config):
    '''
    This function creates the ArgumentParser given current status of config and
    returns args as a dictionary.
    '''
    ap = argparse.ArgumentParser(description='''
    Neuromake is a helper tool designed to clean up snakemake workflows that
    operate on BIDS datasets. This command-line interface prepares a specific
    config file, which is used to manage all variables necessary to run the
    workflow.
    '''.replace('\n','').replace('\t',''))

    ap.add_argument(
        '--reindex',
        action="store_true",
        help='reindex SQL database for BIDSLayout if bids_layout_db specified in snakemake config file'
    )
    ap.add_argument(
        '--make-default-templates',
        action="store_true",
        help='based on current BIDS variables, construct default snakemake templates'
    )
    ap.add_argument(
        '--get-valid-subjects',
        action="store_true",
        help='based on current BIDS variables, update subjects to all those that have all expected BIDS files'
    )
    # for each setting dictionary, users have the option to add a new wildcard,
    # remove a wildcard, set the values for a wildcard, or set a wildcard as required/not
    subparsers = ap.add_subparsers(dest='setting')
    for k,v in config._config.items():
        current_parser = subparsers.add_parser(k,help=v['__metadata__']['help'])
        add_parser = current_parser.add_parser('add',help='add wildcard')
        add_parser.add_argument('label',required=True,help='wildcard label')
        add_parser.add_argument('value',nargs='+',default='',help='set wildcard value(s)')
        remove_parser = current_parser.add_parser('remove',help='remove wildcard')
        remove_parser.add_argument('label',choices=[x for x in v.keys if '__' not in x],required=True,help='wildcard label')
        set_parser = current_parser.add_parser('set',help='set value(s) for specified wildcard')
        set_parser.add_argument('label',choices=[x for x in v.keys if '__' not in x],required=True,help='wildcard label')
        set_parser.add_argument('value',required=True,nargs='+',default='',help='set wildcard value(s)')
        setreq_parser = current_parser.add_parser('set-required')
        setreq_parser.add_argument('label',required=True,help='wildcard label')
        setopt_parser = current_parser.add_parser('set-optional')
        setopt_parser.add_argument('label',required=True,help='wildcard label')

    argcomplete.autocomplete(ap)
    args = vars(ap.parse_args())
    return args
