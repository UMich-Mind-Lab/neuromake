import pytest
import os
import json
import neuromake as nm
import neuromake.utils as nu
import neuromake.exceptions as err
from neuromake.wildcard import Wildcard, PathWildcard
from neuromake.menu import Menu

#
# INITIALIZATION TESTS
#
def test_menu_init():
    '''menu initializes with minimal settings'''
    menu = Menu('settings')
    assert isinstance(menu,Menu)

def test_menu_init_with_wildcard():
    '''menu initializes with supplied wildcard'''
    w = Wildcard('subject','01',{'required':True})
    menu = Menu('settings',w)
    assert menu._wildcards == [w]

def test_menu_init_with_wildcard_subclass():
    '''menu initializes with supplied wildcard subclass'''
    w = PathWildcard('bids','./tests/bids/ds003988')
    menu = Menu('path',w)
    assert menu._wildcards == [w]

def test_menu_init_with_wildcard_list():
    '''menu initializes with supplied wildcard list'''
    w = [
        Wildcard('subject','01',{'required':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('settings',w)
    assert menu._wildcards == w

def test_menu_init_with_wildcard_duplicate_label_error():
    '''menu does not initialize if a duplicate wildcard label exists'''
    w = [
        Wildcard('subject','01',{'required':True}),
        Wildcard('subject','02')
    ]
    try:
        menu = Menu('settings',w)
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_menu_init_with_invalid_wildcard_type_error():
    '''menu does not initialize when wildcard is incorrect type'''
    w = [
        Wildcard('subject','01',{'required':True}),
        {}
    ]
    try:
        menu = Menu('settings',w)
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardTypeError'
    else:
        assert False

#
# Menu.remove_wildcard() tests
#
def test_menu_remove_wildcard():
    '''remove_wildcard function succeeds'''
    w = Wildcard('subject','01')
    menu = Menu('settings',w)
    menu.remove_wildcard('subject')
    assert menu._wildcards == []

def test_menu_remove_wildcard_not_present_error():
    '''remove_wildcard function fails if wildcard_label specified does not exist'''
    w = Wildcard('subject','01')
    menu = Menu('settings',w)
    try:
        menu.remove_wildcard('foo')
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_menu_remove_wildcard_required_error():
    '''remove_wildcard function fails if wildcard is set as required'''
    w = Wildcard('subject','01',{'required':True})
    menu = Menu('settings',w)
    try:
        menu.remove_wildcard('subject')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardRequiredError'
    else:
        assert False

#
# Menu.to_dict() tests
#
def test_menu_to_dict():
    '''menu dict is returned without metadata'''
    w = [
        Wildcard('subject','01',{'required':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    assert menu.to_dict() == {'bids':{'subject':'01','session':'pre'}}

def test_menu_to_dict_with_metadata():
    '''menu dict is returned with metadata'''
    w = [
        Wildcard('subject','01',{'required':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    d = {
        'bids':{
            'subject':'01',
            'session':'pre',
            '__metadata__':{
                'bids':{'wildcard_type':'Wildcard','required':False},
                'subject':{'iterable':False,'required':True,"wildcard_type":"Wildcard"},
                'session':{'iterable':False,'required':False,"wildcard_type":"Wildcard"}
            }
        }
    }
    assert menu.to_dict(metadata=True) == d


#
# Menu.reset() tests
#
def test_menu_reset():
    w = [
        Wildcard('subject','01',{'required':True}),
        Wildcard('session','pre')
    ]
    menu = Menu('bids',w)
    menu.reset()
    assert menu.to_dict() == {'bids':{'subject':None,'session':None}}

def test_menu_reset_with_defaults():
    w = [
        Wildcard('subject','01',{'required':True,'default':'foo'}),
        Wildcard('session','pre',{'default':'bar'})
    ]
    menu = Menu('bids',w)
    menu.reset()
    assert menu.to_dict() == {'bids':{'subject':'foo','session':'bar'}}

#
# Menu.factory_reset() tests
#
def test_menu_factory_reset():
    w = [
        Wildcard('subject','01',{'required':True,'default':'foo'}),
        Wildcard('session','pre',{'default':'bar'})
    ]
    menu = Menu('bids',w)
    menu.factory_reset()
    assert menu.to_dict() == {'bids':{'subject':'foo'}}

def test_menu_factory_reset_force():
    w = [
        Wildcard('subject','01',{'required':True,'default':'foo'}),
        Wildcard('session','pre',{'default':'bar'})
    ]
    menu = Menu('bids',w)
    menu.factory_reset(force=True)
    assert menu.to_dict() == {'bids':{}}
