import pytest
import os
import json
import neuromake as nm
import neuromake.utils as nu
import neuromake.exceptions as err
import neuromake.menu as nmenu

def test_create_bids_menu():
    try:
        bids_menu = nmenu.create_bids_menu('func',level='minimal')
    except:
        assert False
    else:
        assert True

def test_create_bids_menu_incorrect_filetype_valueerror():
    try:
        bids_menu = nmenu.create_bids_menu('foo',level='minimal')
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_create_bids_menu_incorrect_filetype_typeerror():
    try:
        bids_menu = nmenu.create_bids_menu({},level='minimal')
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_create_bids_menu_incorrect_level_error():
    try:
        bids_menu = nmenu.create_bids_menu('anat',level='foo')
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_create_paths_menu():
    try:
        paths_menu = nmenu.create_paths_menu()
    except Exception as e:
        print(e)
        assert False
    else:
        assert True
