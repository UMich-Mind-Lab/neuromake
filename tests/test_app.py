import pytest
from deepdiff import DeepDiff
import os
import json
import neuromake as nm
import neuromake.utils as nu
import neuromake.exceptions as err
from neuromake.wildcard import Wildcard, PathWildcard
from neuromake.menu import Menu
from neuromake.app import App

#
# APP INITIALIZATION TESTS
#

def test_app_init():
    '''app initializes with minimal settings'''
    app = App(name='my_pipeline')
    assert isinstance(app,App)

def test_app_invalid_name_error():
    '''name must be a valid filename (avoid special chars)'''
    try:
        app = App(name='h@ck#rK!d!')
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_app_invalid_name_type():
    '''name must be type str'''
    try:
        app = App(name=1038)
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_app_init_with_config():
    '''app initializes with basic config file, to_dict matches input config'''
    cfg_path = 'tests/config/neuromake_test_config.json'
    app = App(cfg_path=cfg_path)
    with open(cfg_path,'r') as cfg_file:
        cfg = json.load(cfg_file)
    print(json.dumps(cfg,indent=2),json.dumps(app.to_dict(metadata=True),indent=2))
    assert app.to_dict(metadata=True) == cfg

def test_app_invalid_cfg_path_error():
    '''cfg_path must be a valid file, or exist in valid directory'''
    cfg_path = 'my_config.json'
    app = App(cfg_path=cfg_path)

    cfg_path = '/foo/bar/biz/bang/config.json'
    try:
        app = App(cfg_path=cfg_path)
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_app_init_with_menu():
    '''app initializes with menu'''
    w = [
        Wildcard('subject','01',{'required':True,'iterable':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    app = App(name='my_pipeline',menu=menu)
    assert app._menus[0]._wildcards == w

#
# App.to_dict() tests
#
def test_app_to_dict():
    '''app to_dict() (no metadata)'''
    w = [
        Wildcard('subject','01',{'required':True,'iterable':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    app = App(name='my_pipeline',menu=menu)
    d = app.to_dict()
    assert d == {
        'my_pipeline':{
            'bids':{
                'subject':['01'],
                'session':'pre'
            }
        }
    }

def test_app_to_dict_with_metadata():
    '''app to_dict() includes menu metadata'''
    w = [
        Wildcard('subject','01',{'required':True,'iterable':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    app = App(name='my_pipeline',menu=menu)
    d = app.to_dict(True)
    assert d == {
        'my_pipeline':{
            'bids':{
                'subject':['01'],
                'session':'pre',
                '__metadata__':{
                    'bids':{'wildcard_type':'Wildcard','required':False},
                    'subject':{'required':True,'iterable':True,"wildcard_type":"Wildcard"},
                    'session':{'required':False,'iterable':False,"wildcard_type":"Wildcard"}
                }
            }
        }
    }
