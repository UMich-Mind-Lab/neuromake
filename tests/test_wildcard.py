import pytest
import os
import neuromake as nm
import neuromake.utils as nu
import neuromake.exceptions as err
from neuromake.wildcard import Wildcard, PathWildcard, TemplateWildcard

def test_wildcard_initialize_all_defaults():
    '''wildcard initializes with minimal settings'''
    w = Wildcard('subject','01')
    assert w.value == '01'

#set_metadata(self,required=False,var_type=None,min_val=None,max_val=None,valid_values=None,iterable=False):
"""
TESTS FOR METADATA VALIDATION
"""
def test_wildcard_set_metadata_generic_help_field_no_validation():
    '''wildcard successfully sets kwargs'''
    w = Wildcard('subject','01',{'help':'foo'})
    assert w._metadata['help'] == 'foo'

#required
def test_wildcard_set_metadata_required_true():
    w = Wildcard('subject','01',{'required':True})
    assert w._metadata['required'] == True

def test_wildcard_set_metadata_required_type_error():
    '''required must be type bool'''
    try:
        w = Wildcard('subject','01',{'required':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

#var_type
def test_wildcard_set_metadata_var_type_str():
    w = Wildcard('subject','01',{'var_type':'str'})
    assert w._metadata['var_type'] == 'str'

def test_wildcard_set_metadata_var_type_invalid_error():
    '''var_type must be in _METADATA_VALID_VARTYPE'''
    try:
        w = Wildcard('subject','01',{'var_type':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

#min_val
def test_wildcard_set_metadata_min_val():
    w = Wildcard('threshold',.5,{'min_val':0})
    assert w._metadata['min_val'] == 0

def test_wildcard_set_metadata_min_val_with_invalid_var_type_error():
    '''min_val cannot be set with non-numeric var_type'''
    try:
        w = Wildcard('threshold',.5,{'var_type':'str','min_val':0})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_wildcard_set_metadata_min_val_invalid_value_error():
    '''min_val must be numeric var type'''
    try:
        w = Wildcard('threshold',.5,{'min_val':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

#max_val
def test_wildcard_set_metadata_max_val():
    w = Wildcard('threshold',.5,{'max_val':1})
    assert w._metadata['max_val'] == 1

def test_wildcard_set_metadata_max_val_with_invalid_var_type_error():
    '''max_val cannot be set with non-numeric var_type'''
    try:
        w = Wildcard('threshold',.5,{'var_type':'str','max_val':0})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_wildcard_set_metadata_max_val_invalid_value_error():
    '''max_val must be numeric var type'''
    try:
        w = Wildcard('threshold',.5,{'max_val':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_wildcard_set_metadata_max_val_less_than_min_val_error():
    '''max_val must be greater than min_val'''
    try:
        w = Wildcard('threshold',.5,{'max_val':.5,'min_val':.6})
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

#valid
def test_wildcard_set_metadata_valid():
    w = Wildcard('task','gng',{'valid':['rest','gng','mid']})
    assert w._metadata['valid'] == ['rest','gng','mid']

def test_wildcard_set_metadata_minmax_set_with_valid_error():
    '''valid cannot be set with min_val or max_val'''
    try:
        w = Wildcard('threshold',.5,{'max_val':.5,'min_val':.6,'valid':[0,1,2]})
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_wildcard_set_metadata_valid_not_list_error():
    '''"valid" metadata must be type list'''
    try:
        w = Wildcard('threshold',.5,{'valid':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_wildcard_set_metadata_valid_values_incorrect_var_type_error():
    '''"valid" values must match "var_type"'''
    try:
        w = Wildcard('threshold',.5,{'valid':[0,1,2],'var_type':'str'})
    except Exception as exception:
        assert type(exception).__name__ == 'TypeError'
    else:
        assert False

def test_wildcard_set_metadata_default_value_not_in_valid_error():
    '''"default" metadata must be in valid'''
    try:
        w = Wildcard('method',3,{'valid':[1,2,3,4],'default':'foo'})
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_wildcard_set_metadata_default_value_lt_min_val_error():
    '''"default value must be greater than min_val"'''
    try:
        w = Wildcard('method',3,{'min_val':1,'default':0})
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_wildcard_set_metadata_default_value_gt_max_val_error():
    '''default value must be smaller than max_val'''
    try:
        w = Wildcard('method',3,{'max_val':1,'default':2})
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

"""
TESTS FOR SETTING WILDCARD LABEL AND VALUE
"""
def test_wildcard_set_value():
    w = Wildcard('subject','01')
    assert w.value == '01'

def test_wildcard_set_invalid_label_type_error():
    '''label must be type str'''
    try:
        w = Wildcard(['hi'],'01')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardTypeError'
    else:
        assert False

def test_wildcard_set_invalid_label_value_error():
    'label str must be valid python variable'
    try:
        w = Wildcard('invalid var name','01')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_wildcard_set_value_invalid_data_object_error():
    '''value cannot be dictionary, only list (if iterable) or single variables'''
    try:
        w = Wildcard('subject',{'01'})
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardTypeError'
    else:
        assert False

def test_wildcard_set_value_data_type_mismatch_metadata_error():
    '''wildcard value must match var_type metadata'''
    try:
        w = Wildcard('subject',1,{'var_type':'str'})
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardTypeError'
    else:
        assert False

def test_wildcard_set_value_lower_than_min_value_error():
    '''wildcard value must be higher than min_val'''
    try:
        w = Wildcard('threshold',.4,{'min_val':.5})
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_wildcard_set_value_higher_than_max_value_error():
    '''wildcard value must be lower than max_val'''
    try:
        w = Wildcard('threshold',.6,{'max_val':.5})
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_wildcard_set_value_not_in_valid_list_error():
    '''wildcard value must be in valid list'''
    try:
        w = Wildcard('task','gng',{'valid':['rest','mid']})
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_wildcard_set_value_iterable():
    w = Wildcard('subject',['01','02','03','04'],{'iterable':True})
    assert w.value == ['01','02','03','04']

def test_wildcard_set_value_as_list_iterable_false_error():
    '''wildcard value cannot be list if not iterable'''
    try:
        w = Wildcard('task',['gng','rest'])
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

"""
OTHER TESTS
"""
def test_wildcard_append():
    w = Wildcard('subject','01',{'iterable':True})
    w.append('02')
    assert w.to_dict() == {'subject':['01','02']}

def test_wildcard_append_not_iterable_error():
    '''cannot append to wildcard if not specified as iterable'''
    w = Wildcard('subject','01')
    try:
        w.append('02')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardNotIterableError'
    else:
        assert False

def test_wildcard_append_not_valid_error():
    '''cannot append invalid value to wildcard'''
    w = Wildcard('subject','01',{'iterable':True,'var_type':'str'})
    try:
        w.append(2)
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardTypeError'
    else:
        assert False

def test_wildcard_to_dict_no_metadata():
    w = Wildcard('subject','01',{'iterable':True})
    assert w.to_dict() == {'subject':['01']}

def test_wildcard_to_dict_with_metadata():
    w = Wildcard('subject','01',{'iterable':True})
    assert w.to_dict(metadata=True) == {'subject':['01'],'__metadata__':{'subject':{'iterable':True,'required':False,"wildcard_type":"Wildcard"}}}

def test_path_wildcard_valid_filepath():
    w = PathWildcard('bids','./tests/bids/ds003988')
    assert w.value == './tests/bids/ds003988'

def test_path_wildcard_invalid_filepath_error():
    try:
        w = PathWildcard('bids','foo/bar/baz')
    except Exception as exception:
        assert type(exception).__name__ == 'PathNotExistError'
    else:
        assert False

def test_template_wildcard():
    w = TemplateWildcard('funcPrefix','sub-{sub}_task-{func_task}')
    assert w.value == 'sub-{sub}_task-{func_task}'

def test_template_wildcard_invalid_format_braces_error():
    try:
        w = TemplateWildcard('funcPrefix','sub-{sub}_task-{func_task}}')
    except Exception as exception:
        assert type(exception).__name__ == 'ValueError'
    else:
        assert False

def test_template_wildcard_invalid_no_formats_error():
    try:
        w = TemplateWildcard('funcPrefix','plain_text_woohoo')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False

def test_template_wildcard_invalid_filepath_error():
    try:
        w = TemplateWildcard('funcPrefix','data/sub-{subject}_ses-*_task-?!_bold.nii.gz')
    except Exception as exception:
        assert type(exception).__name__ == 'WildcardValueError'
    else:
        assert False
