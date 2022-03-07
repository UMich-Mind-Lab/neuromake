import pytest
import os
import neuromake as nm
import neuromake.utils as nu

#multireplace
def test_multireplace_all_replaced():
    assert nu.multireplace('abcabcdabcde',{'ab':'zz'}) == 'zzczzcdzzcde'

def test_multireplace_must_match_end():
    assert nu.multireplace('appappleapp',{'app':'zzz'},match_end=True) == 'appapplezzz'

def test_multireplace_escape_characters():
    assert nu.multireplace('[a].(b).{c}.`d`',{'[a]':'a','.':' ','(b)':'b','{c}':'c','`d`':'d'}) == 'a b c d'

def test_multireplace_later_key_superceded_by_previous_key():
    assert nu.multireplace('abcdef',{'ab':'z','bc':'y'}) == 'zcdef'

def test_multireplace_blah():
    assert nu.multireplace('recording',{'rec':'reconstruction'},match_end=True) == 'recording'

#get_n_combos_per_subject
def test_get_n_combos_per_subject_main():
    assert nu.get_n_combos_per_subject({'subject':'1','session':['1','2'],'task':['mid','nback','rest']}) == 6

#get_bids_vars_dict
def test_get_bids_vars_dict_main():
    assert nu.get_bids_vars_dict('sub-1_ses-2_task-mid_acq-multiband_run-1_bold.nii.gz') == {'subject':'1','session':'2','func_task':'mid','func_acquisition':'multiband','func_run':'1','func_suffix':'bold','extension':'nii.gz'}

def test_get_bids_vars_dict_add_prefix_false():
    assert nu.get_bids_vars_dict('sub-1_ses-2_task-mid_acq-multiband_run-1_bold.nii.gz',add_prefix=False) == {'subject':'1','session':'2','task':'mid','acquisition':'multiband','run':'1','suffix':'bold','extension':'nii.gz'}

def test_get_bids_vars_dict_physio_add_prefix_false():
    assert nu.get_bids_vars_dict('sub-1_ses-2_task-mid_acq-multiband_run-1_recording-cardiac_physio.tsv.gz',add_prefix=False) == {'subject':'1','session':'2','task':'mid','acquisition':'multiband','run':'1','suffix':'physio','extension':'tsv.gz','recording':'cardiac'}

def test_get_bids_vars_dict_physio():
    assert nu.get_bids_vars_dict('sub-1_ses-2_task-mid_acq-multiband_run-1_recording-cardiac_physio.tsv.gz') == {'subject':'1','session':'2','func_task':'mid','func_acquisition':'multiband','func_run':'1','physio_suffix':'physio','extension':'tsv.gz','physio_recording':'cardiac'}

def test_query_bids_layout_sub01_func():
    config = nm.Config('./tests/config/ex_ds003988.json')
    files = nu.query_bids_layout(config.layout,{'subject':'01','run':'1','suffix':'bold'})
    files = [ os.path.basename(x.filename) for x in files]
    assert files == ['sub-01_task-read_run-1_bold.nii.gz']
