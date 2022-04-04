"""Wildcard class to manage individual wildcard variables"""
from pathlib import Path
import re
from string import Formatter
import neuromake.exceptions as err

class Wildcard():
    '''a single variable within a neuromake menu'''
    def __init__(self,label,value,metadata={}):
        self._set_metadata_defaults()
        self.set_metadata(**metadata)
        self.label = label
        self.value = value

    def to_dict(self,metadata=False):
        '''
        returns wildcard object as dictionary, where key = Label and val = Value

        metadata (bool): If True, include metadata in dictionary under key
        "__metadata__" (default: False)
        '''
        d = {self.label:self.value}
        if metadata:
            m = { k:v for k,v in self._metadata.items() if v is not None }
            d['__metadata__'] = {self.label:m}
            d['__metadata__'][self.label]['wildcard_type'] = type(self).__name__
        return d

    def _set_metadata_defaults(self):
        '''set metadata defaults for Wildcard'''
        self._METADATA_VALID_VARTYPE = ['int','float','bool','str']
        self._METADATA_DEFAULTS = {
            'help':None,
            'required':False,
            'default':None,
            'var_type':None,
            'min_val':None,
            'max_val':None,
            'valid':None,
            'iterable':False
        }
        self._metadata = self._METADATA_DEFAULTS

    def set_metadata(self,**kwargs):
        f'''
        set metadata for wildcard variable, The following options:

        help: (str) specify help text for wildcard.
            DEFAULT: {self._METADATA_DEFAULTS["help"]}
        required: (bool) specify if wildcard is required within associated Menus
            DEFAULT: {self._METADATA_DEFAULTS["required"]}
        default: specify default value for wildcard
            DEFAULT: {self._METADATA_DEFAULTS["default"]}
        var_type: (string) specify valid variable type for value
            OPTIONS: {self._METADATA_VALID_VARTYPE}
            DEFAULT: {self._METADATA_DEFAULTS["var_type"]}
        min_val: (numeric) minimum valid value for wildcard.
            DEFAULT: {self._METADATA_DEFAULTS["min_val"]}
        max_val: (numeric) maximum valid value for wildcard
            DEFAULT: {self._METADATA_DEFAULTS["max_val"]}
        valid: (list of <type>) array of valid options for value
            DEFAULT: {self._METADATA_DEFAULTS["valid"]}
        iterable: (bool) specify if value should be singular or multiple.
            DEFAULT: {self._METADATA_DEFAULTS["iterable"]}

        In addition, one can specify any arbitrary **kwargs to define other
        metadata, though these will not be used for any internal validation
        logic.
        '''
        metadata = self._METADATA_DEFAULTS
        metadata.update(self._metadata)
        metadata.update(kwargs)

        if metadata['help'] is not None and not(isinstance(metadata['help'],str)):
            raise TypeError('"help" metadata must be type str.')
        if not(isinstance(metadata['required'],bool)):
            raise TypeError('"required" metadata must be type bool.')
        if not(isinstance(metadata['iterable'],bool)):
            raise TypeError('"iterable" metadata must be type bool.')
        if metadata['var_type'] is not None:
            if metadata['var_type'] not in self._METADATA_VALID_VARTYPE:
                raise TypeError(f'"var_type" must be one of {self._METADATA_VALID_VARTYPE}.')

        if metadata['min_val'] is not None:
            if metadata['var_type'] is not None and metadata['var_type'] not in ['int','float']:
                raise TypeError(f'"var_type" metadata must be int or float if "min_val" is set.')
            min_val_type = type(metadata['min_val']).__name__
            if min_val_type not in ['int','float']:
                raise TypeError(f'"min_val" metadata must be int or float, not {min_val_type}.')

        if metadata['max_val'] is not None:
            if metadata['max_val'] is not None:
                if metadata['var_type'] is not None and metadata['var_type'] not in ['int','float']:
                    raise TypeError(f'"var_type" metadata must be int or float if "max_val" is set.')
                max_val_type = type(metadata['max_val']).__name__
                if max_val_type not in ['int','float']:
                    raise TypeError(f'"max_val" metadata must be int or float, not {max_val_type}.')
            if metadata['min_val'] is not None:
                if metadata['min_val'] >= metadata['max_val']:
                    raise ValueError(f'"max_val" metadata ({metadata["max_val"]}) cannot be smaller than "min_val" ({metadata["min_val"]}).')

        if metadata['valid'] is not None:
            if metadata['min_val'] is not None or metadata['max_val'] is not None:
                raise ValueError('"valid" cannot be set with "min_val" or "max_val".')
            if not(isinstance(metadata['valid'],list)):
                raise TypeError('"valid" must be type list.')
            if metadata['var_type'] is not None:
                for v in metadata['valid']:
                    if type(v).__name__ != metadata['var_type']:
                        raise TypeError(f'{v} does not match required type {metadata["var_type"]}')

        if metadata['default'] is not None:
            if metadata['min_val'] is not None and metadata['default'] <= metadata['min_val']:
                raise ValueError('default must be larger than min_val.')
            if metadata['max_val'] is not None and metadata['default'] >= metadata['max_val']:
                raise ValueError('default must be smaller than max_val')
            if metadata['valid'] is not None and metadata['default'] not in ['valid']:
                raise ValueError('default must be in valid.')
            if metadata['var_type'] is not None and not(type(metadata['default']).__name__ == metadata['var_type']):
                raise TypeError(f'default must be type {metadata["var_type"]}.')

        self._metadata = metadata

    @property
    def label(self):
        '''
        label for wildcard variable. This is the format string that will be
        used to access <value> within snakemake
        '''
        return self._label

    @label.setter
    def label(self,label):
        self._label_validation(label)
        self._label = label

    def _label_validation(self,label):
        '''
        validation for wildcard label. Labels must:
        1. be a str type
        2. be a valid python variable name
        '''
        if not(isinstance(label,str)):
            raise err.WildcardTypeError(f'label must be str, not {type(label).__name__}')
        if label != re.sub(r'\W|^(?=\d)','',label):
            raise err.WildcardValueError(f'"{label}" is an invalid wildcard label (must be valid python variable).')

    @property
    def value(self):
        '''wildcard variable value. Can be a '''
        return self._value

    @value.setter
    def value(self,value):
        '''set wildcard variable value'''
        self._value_validation(value)
        if isinstance(value,list):
            self._value = value
        elif 'iterable' in self._metadata.keys() and self._metadata['iterable']:
            self._value = [value]
        else:
            self._value = value

    def append(self,value):
        '''
        if wildcard is iterable, append target value to value list
        '''
        if self._metadata['iterable']:
            self._value_validation(value)
            self._value.append(value)
        else:
            raise err.WildcardNotIterableError(f'wildcard {self.label} is not iterable and cannot be appended to.')

    def _value_validation(self,value):
        '''validate wildcard values prior to setting. Values must conform with
        any specific metadata fields.'''
        if value is not None:
            if not(isinstance(value,list)):
                if type(value).__name__ in self._METADATA_VALID_VARTYPE:
                    value = [value]
                else:
                    raise err.WildcardTypeError(f'Invalid data type for {value} {type(value)}.')
            for v in value:
                if self._metadata['var_type'] is not None:
                    valtype = type(v).__name__
                    if valtype != self._metadata['var_type']:
                        raise err.WildcardTypeError(f'{v} is type {valtype} but should be {self._metadata["var_type"]}.')
                if self._metadata['min_val'] is not None:
                    if v < self._metadata['min_val']:
                        raise err.WildcardValueError(f'{v} is lower than minimum ({self._metadata["min_val"]}).')
                if self._metadata['max_val'] is not None:
                    if v > self._metadata['max_val']:
                        raise err.WildcardValueError(f'{v} is higher than maximum ({self._metadata["max_val"]}).')
                if self._metadata['valid'] is not None:
                    if v not in self._metadata['valid']:
                        raise err.WildcardValueError(f'{v} is invalid, must be one of {self._metadata["valid"]}.')
            if not(self._metadata['iterable']) and len(value) > 1:
                raise err.WildcardValueError(f'{value} cannot be iterable.')

class PathWildcard(Wildcard):
    '''
    wildcard object for paths. Adds filepath validation to value setter
    '''
    def _set_metadata_defaults(self):
        '''set metadata defaults for Wildcard'''
        self._METADATA_VALID_VARTYPE = ['str']
        self._METADATA_DEFAULTS = {
            'help':None,
            'required':False,
            'default':None,
            'var_type':'str',
            'min_val':None,
            'max_val':None,
            'valid':None,
            'iterable':False
        }
        self._metadata = self._METADATA_DEFAULTS

    def _value_validation(self,value):
        '''
        beyond standard validation, directory wildcard value must:

        1. be a valid path/file
        '''
        super()._value_validation(value)
        if value is not None:
            if isinstance(value,list):
                for v in value:
                    self._value_validation(v)
            else:
                if not(Path(value).exists()):
                    raise err.PathNotExistError(value)


class TemplateWildcard(Wildcard):
    '''
    wildcard object for templates. Adds filepath validation to value setter
    '''
    def _set_metadata_defaults(self):
        '''set metadata defaults for Wildcard'''
        self._METADATA_VALID_VARTYPE = ['str']
        self._METADATA_DEFAULTS = {
            'help':None,
            'required':False,
            'default':None,
            'var_type':'str',
            'min_val':None,
            'max_val':None,
            'valid':None,
            'iterable':False
        }
        self._metadata = self._METADATA_DEFAULTS


    def _value_validation(self,value):
        '''
        beyond standard validation, template wildcard value must:

        1. have at least one valid format field
        2. be a valid filename ()

        Ensuring that fields only have variables set in BIDS will happen at the
        App level, as it requires access to the BIDS menu.
        '''
        super()._value_validation(value)
        if value is not None:
            if isinstance(value,list):
                for v in value:
                    self._value_validation(v)
            else:
                fields = [fname for _,fname,_,_ in Formatter().parse(value) if fname ]
                if len(fields) == 0:
                    raise err.WildcardValueError(f'template wildcards must have at least one format field.')
                valid_str = "".join(i for i in value if i not in r"\:*?<>| ")
                if value != valid_str:
                    raise err.WildcardValueError(f'template wildcard value ("{value}") contains illegal characters.')
