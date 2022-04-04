"""menu object, hosting a collection of associated metadata files"""
import re
from neuromake.wildcard import Wildcard, PathWildcard, TemplateWildcard
import neuromake.exceptions as err

class Menu:
    """Menu with associated Wildcards"""
    def __init__(self,name,wildcard=None,metadata=None):
        self._WILDCARD_TYPES = ['Wildcard','PathWildcard','TemplateWildcard']
        self._name = name
        self._set_metadata_defaults()
        if metadata is not None:
            if isinstance(metadata,dict):
                self.set_metadata(**metadata)
            else:
                raise TypeError(f'"metadata" must be type dict, not {type(metadata).__name__}.')

        self._wildcards = []
        if wildcard is not None:
            self.add_wildcard(wildcard)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,name):
        self._validate_name(name)
        self._name = name

    def _validate_name(self,name):
        '''
        validation for menu name:

        1. must be string
        2. must be alphanumeric
        '''
        if not(isinstance(name,str)):
            raise TypeError(f'Menu name must be type str, not {type(name).__name}.')
        if not(name.isalnum()):
            raise ValueError('"name" must be alphanumeric.')

    def _set_metadata_defaults(self):
        '''set metadata defaults for Menu instance'''
        self._METADATA_DEFAULTS = {
            'help':None,
            'required':False,
            'valid_labels':None,
            'wildcard_type':'Wildcard',
        }
        self._metadata = self._METADATA_DEFAULTS

    def set_metadata(self,**kwargs):
        '''
        set metadata for Menu object. Fields include:

        help: (str) specify help text for Menu
        valid_labels: (list of str) specify valid wildcard labels for menu. If None,
        any wildcard label is permissable [default: None]
        wildcard_type: (string class name) specify wildcard class that is valid
        for the particular menu. OPTIONS: ["Wildcard","PathWildcard",
        "TemplateWildcard"], where Wildcard allows any type of wildcard instance,
        but PathWildcard/TemplateWildcard limit it to only that type of
        Wildcard.
        **kwargs: any other metadata fields to specify. By default, these will
        not be incorporated into any neuromake logic
        '''
        metadata = self._metadata.copy()
        metadata.update(kwargs)

        if metadata['help'] is not None:
            if not(isinstance(metadata['help'],str)):
                raise TypeError('metadata "help" must be type str.')

        if metadata['valid_labels'] is not None:
            if not(isinstance(metadata['valid_labels'],list)):
                raise TypeError('metadata "valid_labels" must be type list.')
            for v in metadata['valid_labels']:
                if not(isinstance(v,str)):
                    raise err.WildcardTypeError(f'"{v}" is an invalid wildcard type (must be type str).')
                if v != re.sub(r'\W|^(?=\d)','', v):
                    raise err.WildcardValueError(f'"{v}" is an invalid wildcard name (must be valid python variable).')

        if metadata['wildcard_type'] not in self._WILDCARD_TYPES:
            raise ValueError(f'"valid_wildcard_type" must be one of {self._WILDCARD_TYPES}.')

        self._metadata = metadata

    def add_wildcard(self,wildcard):
        '''add Wildcard (or list of Wildcards) to Menu'''
        if isinstance(wildcard,list):
            for w in wildcard:
                self.add_wildcard(w)
        else:
            self._validate_wildcard(wildcard)
            self._wildcards.append(wildcard)

    def _validate_wildcard(self,wildcard):
        '''
        perform validation checks prior to adding wildcard:
        1. wildcard must match metadata wildcard_type
        2. wildcard cannot have same label as existing wildcard within Menu
        '''
        if self._metadata['wildcard_type'] == 'Wildcard':
            if not(isinstance(wildcard,Wildcard)):
                raise err.WildcardTypeError(f'wildcard must be type "Wildcard", not {type(wildcard).__name__}.')
        elif self._metadata['wildcard_type'] == 'PathWildcard':
            if not(isinstance(wildcard,PathWildcard)):
                raise err.WildcardTypeError(f'wildcard must be type "PathWildcard".')
        elif self._metadata['wildcard_type'] == 'TemplateWildcard':
            if not(isinstance(wildcard,TemplateWildcard)):
                raise err.WildcardTypeError(f'wildcard must be type "TemplateWildcard".')

        if wildcard.label in [ w.label for w in self._wildcards ]:
            raise err.WildcardValueError(f'Wildcard "{wildcard.label}" already exists in Menu {self.name}.')

    def _validate_wildcard_label(self,wildcard_label):
        '''
        perform validation checks prior to referencing wildcard_label
        1. wildcard_label must be a str instance
        2. wildcard_label must exist for a wildcard in _wildcards
        '''
        if not(isinstance(wildcard_label,str)):
            raise TypeError(f'wildcard_label must be str, not {type(wildcard_label).__name__}.')
        if not(wildcard_label in [ w.label for w in self._wildcards ]):
            raise ValueError(f'"{wildcard_label}" not found in wildcards.')

    def get_wildcard(self,wildcard_label):
        '''retreive wildcard from menu'''
        self._validate_wildcard_label(wildcard_label)
        return [ w for w in self._wildcards if w.label == wildcard_label ][0]

    def remove_wildcard(self,wildcard_label):
        '''remove Wildcard (or list of Wildcards) to Menu'''
        w = self.get_wildcard(wildcard_label)
        if w._metadata['required']:
            raise err.WildcardRequiredError(f'"{w.label}" is required and cannot be removed.')
        self._wildcards.remove(w)

    def reset(self):
        '''
        clear values for all wildcard variables, set values to defaults if present.
        '''
        for w in self._wildcards:
            w.value = w._metadata['default']

    def factory_reset(self,force=False):
        '''
        remove all non-required wildcards from Menu. Set required wildcards to
        default values.

        force: (bool) remove required wildcards too. [DEFAULT: False]
        '''
        if force:
            self._wildcards = []
            self._metadata = {}
        else:
            n_required = len([w for w in self._wildcards if w._metadata['required']])
            i = 0
            while len(self._wildcards) > n_required:
                if self._wildcards[i]._metadata['required']:
                    self._wildcards[i].value = self._wildcards[i]._metadata['default']
                    i += 1
                else:
                    self._wildcards.remove(self._wildcards[i])

    def to_dict(self,metadata=False):
        '''
        get all wildcards labels and values within Menu as dict.

        metadata: (bool) return metadata [DEFAULT: False]
        '''
        d = {}
        if metadata:
            d['__metadata__'] = {self.name:{ k:v for k,v in self._metadata.items() if v is not None }}
        for w in self._wildcards:
            wildcard_dict = w.to_dict(metadata=metadata)
            if metadata:
                d['__metadata__'] = {**d['__metadata__'],**wildcard_dict.pop('__metadata__')}
            d.update(wildcard_dict)
        return {self.name:d}
