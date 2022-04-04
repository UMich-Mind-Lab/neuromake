"""Config class to manage changes to config file"""
import os
import json
from neuromake.menu import Menu
from neuromake.wildcard import Wildcard, PathWildcard, TemplateWildcard
import neuromake.exceptions as err

class App:
    '''
    Neuromake.App controls menu initialization
    '''
    def __init__(self,cfg_path=None,sm_cfg_path=None,name=None,menu=None,metadata=None):
        '''
        cfg_path: (str,path) path for app configuration file
        sm_cfg_path: (str,path) path for snakemake configuration file
        name: (str) name of neuromake app
        menu: Menu or list of Menus [Default: None ]
        '''
        self._name = ""
        if name is not None:
            self.name = name

        self._menus = []
        if menu is not None:
            self.add_menu(menu)

        self.cfg_path = cfg_path
        if self._cfg_path is not None and os.path.isfile(self._cfg_path):
            self._load_from_config()

        self.sm_cfg_path = sm_cfg_path

    @property
    def name(self):
        '''
        (str) name of neuromake App
        '''
        return self._name

    @name.setter
    def name(self,name):
        self._validate_name(name)
        self._name = name

    def _validate_name(self,name):
        '''
        App Name must

        1. Be a str instance
        2. only contain alphanumeric or "_-. " characters
        '''
        if not(isinstance(name,str)):
            raise TypeError(f'"name" must be type str, not {type(name).__name__}.')
        for x in name:
            if not(x.isalnum()) and not(x in "._- "):
                raise ValueError(f'"name" contains invalid character "{x}". Name must be comprised of alphanumeric characters or "._- " only.')

    @property
    def cfg_path(self,cfg_path):
        '''
        (str,Path) path to App config file in json format. if file does not
        exist, will set the path as the default save path for this app instance)
        '''
        return self._cfg_path

    @cfg_path.setter
    def cfg_path(self,cfg_path):
        self._validate_cfg_path(cfg_path)
        self._cfg_path = cfg_path

    def _validate_cfg_path(self,cfg_path):
        '''
        if cfg_path is not None, it must

        1. be a string instance
        2. point to a valid file OR be a valid directory
        '''
        if cfg_path is not None:
            if not(isinstance(cfg_path,str)):
                raise TypeError(f'"cfg_path" must be type str, not {type(cfg_path).__name__}.')
            if not(os.path.isfile(cfg_path)):
                cfg_dir = os.path.dirname(cfg_path)
                if not(os.path.isdir(cfg_dir) or cfg_dir == ''):
                    raise ValueError(f'"{cfg_path}": no such file or directory.')

    @property
    def sm_cfg_path(self,sm_cfg_path):
        '''
        (str,Path) path to App config file in json format. if file does not
        exist, will set the path as the default save path for this app instance)
        '''
        return self._sm_cfg_path

    @sm_cfg_path.setter
    def sm_cfg_path(self,sm_cfg_path):
        self._validate_cfg_path(sm_cfg_path)
        self._sm_cfg_path = sm_cfg_path

    def _validate_sm_cfg_path(self,sm_cfg_path):
        '''
        if cfg_path is not None, it must

        1. be a string instance
        2. point to a valid file OR be a valid directory
        '''
        if sm_cfg_path is not None:
            if not(isinstance(sm_cfg_path,str)):
                raise TypeError(f'"{sm_cfg_path}" must be type str, not {type(sm_cfg_path).__name__}.')
            if not(os.path.isfile(sm_cfg_path)):
                cfg_dir = os.path.dirname(sm_cfg_path)
                if not(os.path.isdir(sm_cfg_dir) or sm_cfg_dir == ''):
                    raise ValueError(f'"{sm_cfg_path}": no such file or directory.')

    def _load_from_config(self):
        '''
        load a neuromake App instance from config file
        '''
        with open(self._cfg_path,'r') as cfg_file:
            data = json.load(cfg_file)

        if len(data.keys()) != 1:
            raise err.AppConfigError(f'app config should have 1 key (app name)')
        self.name = next(iter(data.keys()))

        menus = []

        for menu_name,menu_data in data[self.name].items():
            metadata = menu_data.pop('__metadata__',{})
            menu_metadata = metadata.pop(menu_name)
            wildcards = []
            for wc_label,wc_value in menu_data.items():
                # make sure menu wildcard type matches wildcard type, if not
                # generic wildcards
                menu_wc_type = menu_metadata['wildcard_type']
                wc_type = metadata[wc_label].pop('wildcard_type')
                if menu_wc_type != 'Wildcard':
                    if menu_wc_type != wc_type:
                        raise err.AppConfigError(f'Menu {menu_name} expects {menu_wc_type}s, not {wc_type}s.')
                # now  generate wildcard objects
                if wc_type == 'Wildcard':
                    w = Wildcard(wc_label,wc_value,metadata[wc_label])
                elif wc_type == 'PathWildcard':
                    w = PathWildcard(wc_label,wc_value,metadata[wc_label])
                elif wc_type == 'TemplateWildcard':
                    w = TemplateWildcard(wc_label,wc_value,metadata[wc_label])
                else:
                    raise err.AppConfigError(f'Unknown wildcard_type provided ({wc_type}).')
                wildcards.append(w)
            menus.append(Menu(menu_name,wildcard=wildcards,metadata=menu_metadata))
        self.add_menu(menus)

    def add_menu(self,menu):
        '''
        add menu(s) to App.
        '''
        if isinstance(menu,list):
            for m in menu:
                self._validate_menu(m)
                self._menus.append(m)
        else:
            self._validate_menu(menu)
            self._menus.append(menu)

    def get_menu(self,menu_name):
        '''
        get menu from neuromake app instance.
        '''
        for menu in self._menus:
            if menu.name == menu_name:
                return menu
        raise ValueError(f'"{menu_name}" is not a valid menu_label.')

    def remove_menu(self,menu_label):
        '''
        permanently remove menu_label from neuromake app instance.
        '''
        self._menus.remove(self.get_menu(menu_label))

    def _validate_menu(self,menu):
        '''
        1. must be of type Menu
        2. name must not already exist in menus
        '''
        if not(isinstance(menu,Menu)):
            raise TypeError(f'menu must be type Menu, not {type(menu).__name__}.')
        if menu.name in [ x.name for x in self._menus ]:
            raise ValueError(f'duplicate menu name "{m.name}".')

    def to_dict(self,metadata=False,header=True):
        '''
        return dictionary with all app data

        metadata: (bool) include metadata [DEFAULT: False]
        header: (bool) include name of App as header [DEFAULT: False]

        Both should be true for saving an App config, and both should be false
        when saving the config file for snakemake's reference.
        '''
        d = {}
        for menu in self._menus:
            d.update(menu.to_dict(metadata=metadata))
        return {self.name:d}
