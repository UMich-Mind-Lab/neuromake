import pytest
import os
import neuromake as nm
import neuromake.utils as nu
import neuromake.cli as cli
import neuromake.exceptions as err

def test_cli_parser_ds003988_add_bids_var_acquisition():
    config = nm.Config('./tests/config/ex_ds003988.json')
    args = cli.parse_args(config,args=['--dry-run','bids','add','acquisition','multiband'])
    shouldbe = {'menu':'bids','action':'add','label':'acquisition','value':['multiband'],'dry_run':True,'get_valid_subjects':False,'make_default_templates':False,'reindex':False,'verbosity':False}
    assert args == shouldbe

def test_cli_parser_ds003988_set_required_bids_var_acquisition():
    config = nm.Config('./tests/config/ex_ds003988.json')
    args = cli.parse_args(config,args=['--dry-run','bids','set-required','acquisition'])
    shouldbe = {'menu':'bids','action':'set-required','label':'acquisition','value':[],'dry_run':True,'get_valid_subjects':False,'make_default_templates':False,'reindex':False,'verbosity':False}
    assert args == shouldbe

def test_cli_ds003988_bids_add_func_acquisition_multiband():
    config = nm.Config('./tests/config/ex_ds003988.json')
    cli.cli(config,args=['--dry-run','bids','add','func_acquisition','multiband'])
    assert config.config['bids']['func_acquisition'] == ['multiband']

def test_cli_ds003988_bids_add_bids_invalid_label():
    config = nm.Config('./tests/config/ex_ds003988.json')
    try:
        cli.cli(config,args=['--dry-run','bids','add','foo'])
    except err.InvalidMenuLabelError:
        assert True
    except:
        assert False

def test_cli_ds003988_bids_set_subject_list():
    config = nm.Config('./tests/config/ex_ds003988.json')
    cli.cli(config,args=['--dry-run','bids','set','subject','01','02','03'])
    assert config.config['bids']['subject'] == ['01','02','03']

def test_cli_ds003988_bids_set_invalid_label():
    config = nm.Config('./tests/config/ex_ds003988.json')
    try:
        cli.cli(config,args=['--dry-run','bids','set','foo','bar'])
    except err.InvalidMenuLabelError:
        assert True
    except:
        assert False

def test_cli_ds003988_bids_set_required_func_task():
    config = nm.Config('./tests/config/ex_ds003988.json')
    cli.cli(config,args=['--dry-run','bids','set-required','func_task'])
    assert 'func_task' in config.config['bids']['__metadata__']['required']

def test_cli_ds003988_bids_set_required_invalid_label():
    config = nm.Config('./tests/config/ex_ds003988.json')
    try:
        cli.cli(config,args=['--dry-run','bids','set-required','foo'])
    except err.InvalidMenuLabelError:
        assert True
    except:
        assert False

def test_cli_ds003988_bids_set_optional_subject():
    config = nm.Config('./tests/config/ex_ds003988.json')
    cli.cli(config,args=['--dry-run','bids','set-optional','subject'])
    assert 'subject' not in config.config['bids']['__metadata__']['required']

def test_cli_ds003988_bids_set_optional_invalid_label():
    config = nm.Config('./tests/config/ex_ds003988.json')
    try:
        cli.cli(config,args=['--dry-run','bids','set-optional','foo'])
    except err.InvalidMenuLabelError:
        assert True
    except:
        assert False
