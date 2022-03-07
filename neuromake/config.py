"""Config class to manage changes to config file"""
import os
import json
import time
import re
import pkg_resources
from collections import Counter
from string import Formatter
from bids import BIDSLayout
import neuromake.utils as nu
import neuromake.exceptions as err


def debug(func):
    def dec(*args,**kwargs):
        print(func.__name__)
        print(args,kwargs)
        results = func(*args,**kwargs)
        print(results)
        return results
    return dec

class Config():
    def __init__(self,fpath=None,reindex=False):
        self._load_bidsKeyNames()
        self._load_bidsFileTypes()
        self._log = []
        self._configPath = fpath
        if self._configPath is not None:
            with open(self._configPath,'r') as fp:
                self.config = json.load(fp)
            self.get_bids_layout(reindex=reindex)
        # TODO: validate config

    def _load_bidsKeyNames():
        '''set self._bidsKeyNames from package json file'''
        stream = pkg_resources.resource_stream(__name__,'config/keynames.json')
        self._bidsKeyNames = json.load(stream)

    def _load_bidsFileTypes():
        '''set self._bidsFileTypes from package json file'''
        stream = pkg_resources.resource_stream(__name__,'config/filetypes.json')
        self._bidsFileTypes = json.load(stream)

    def get_bids_vars(self,filetype=None):
        '''
        when constructing templates, there is a typical order for key-val pairs
        to go into. This function retrieves all config['bids'].keys() in this
        specified order
        '''
        v = []
        for x in self.config['bids']['__metadata__']['valid']:
            if x in self.config['bids'].keys():
                if filetype is None:
                    v.append(x)
                else:
                    if filetype in x:
                        v.append(x)
                    elif x in ['subject','session']:
                        v.append(x)
        return v

    def get_bids_filetypes(self):
        '''
        return the unique filetypes available in bidsVars, which are currently
        anat, func, fmap, dwi, physio
        '''
        v = self.get_bids_vars()
        return set([ x.split('_')[0] for x in v if '_' in x ])

    def get_bids_filetype(self,bidsfile):
        '''
        return the filetype from the bidsfile
        '''
        d = {"<label>":"[0-9A-Za-z]+","<index>":"[0-9]+","<suffix>":"[0-9A-Za-z]+","<matches>":"[0-9A-Za-z_-]+","\[":"(","\]":")?"}
        bidsfile = os.path.basename(bidsfile)
        matches = []
        for k,v in self._bidsFileTypes.items():
            if any([ re.match(nu.multireplace(re.escape(t),d),bidsfile) for t in v['templates']]):
                matches.append(k)
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            return matches

    def get_bids_key_val_pairs(self,filetype):
        '''
        returns a list of variables in the proper order for constructing generic
        template strings.
        '''
        vars = self.get_bids_vars(filetype)
        rep = { filetype+'_':'' }
        rep.update({k:v for k,v in self._bidsKeyNames.items()})
        out = []
        for x in vars:
            if 'suffix' in x:
                out.append('{'+x+'}')
            else:
                out.append(f'{nu.multireplace(x,rep)}-'+'{'+x+'}')
        return out

    def is_valid_template(self,template):
        '''
        performs a simple checks to determine if x has format strings that match
        bidsvars
        '''
        fields = [x for _, x, _, _ in Formatter().parse(template) if x]
        if len(fields) == 0:
            return False
        else:
            return all([ x in self.config['bids'].keys() for x in fields ])

    def make_default_templates(self):
        '''
        creates default templates for config. There will be a template for each
        bids filetype, including each variable included in that filetype
        '''
        fTypes = self.get_bids_filetypes()
        d = {}
        for t in fTypes:
            vars = self.get_bids_key_val_pairs(t)
            prefix = f'{"_".join(vars).replace(f"{t}_suffix-","")}'
            self.config['templates'][f'{t}Prefix'] = prefix

    def get_bids_layout(self,reindex=False):
        #print(f'[{time.strftime("%H:%M:%S")}]','Resetting indexed bids layout database...')
        self.layout = BIDSLayout(
            self.config['directories']['bids'],
            database_path=self.config['directories']['bidslayout'],
            reset_database=reindex)
        #print(f'[{time.strftime("%H:%M:%S")}]','Done.')

    def get_valid_subjects(self):
        '''
        based on currently available BIDS variables, search for all subs in
        bidslayout matching those variables
        '''
        fTypes = self.get_bids_filetypes()
        rep = { f'{x}_':'' for x in fTypes}
        dSubs = {k:v for k,v in self.config['bids'].items() if k in ['session']}
        self._log.append(f'[{time.strftime("%H:%M:%S")}]: querying BIDS layout for subjects...')
        self.config['bids']['subject'] = self.layout.get_subjects(**dSubs)

        # for each type of file needed, we'll look at the parameters to see how
        # many files are expected. If the number of files found matches, then
        # we'll label the subject as valid
        nExpected = 0
        c = Counter([])
        allFiles = []
        for fType in fTypes:
            vars = self.get_bids_vars(fType)
            d = { k:v for k,v in self.config['bids'].items() if k in vars }
            d = nu.multireplace_dict_keys(d,rep,match_end=True)
            if fType in ['anat','func','dwi','fmap']:
                d.update({'extension':'nii.gz'})
            elif fType == 'physio':
                d.update({'extension':'tsv.gz'})
            self._log.append(f'[{time.strftime("%H:%M:%S")}]: querying BIDS layout for {fType} files...')
            fFiles = self.layout.get(**d)
            nExpected += nu.get_n_combos_per_sub(d)

            # we don't want all matches for fmaps, only those whose IntendedFor
            # matches a previous file
            if fType == 'fmap':
                validFmaps = []
                for fmap in fFiles:
                    try:
                        for i in fmap.get_metadata()['IntendedFor']:
                            if any([ i in x.path for x in allFiles ]):
                                validFmaps.append(fmap)
                    except:
                        validFmaps.append(fmap) #well, we tried.
                c += Counter([ nu.get_bids_vars_dict(x.path)['subject'] for x in validFmaps])
            elif fType == 'physio':
                validPhysio = []
                # prep a version of all files so that suffix.extension is removed
                # help us find physio matches
                matches = [ '_'.join(x.path.split('_')[:-1]) for x in allFiles ]
                for physio in fFiles:
                    if any([ x in physio.path for x in matches]):
                        validPhysio.append(physio)
                c += Counter([ nu.get_bids_vars_dict(x.path)['subject'] for x in validPhysio])
            else:
                allFiles.extend(fFiles)
                c += Counter([ nu.get_bids_vars_dict(x.path)['subject'] for x in fFiles])

        # loop through counter to find subjects that have the right number of files
        subjects = []
        for k,v in dict(c).items():
            if v == nExpected:
                subjects.append(k)
            else:
                self._log.append(f'subject {k} not included. Has {v} of {nExpected} required files.')
        self.config['bids']['subject'] = subjects
        self.config['bids']['subject'].sort()

    def add_setting_key(self,setting,key,val=None):
        '''add new key within setting dictionary'''
        if not(setting in self.config.keys()):
            raise err.InvalidSettingError(setting)
        if 'valid' in self.config[setting]['__metadata__'].keys():
            if not(key in self.config[setting]['__metadata__']['valid']):
                raise ValueError(f'{key} is not valid for {setting}.')
        if val is not None:
            if setting == 'directories' and not(os.path.exists(val)):
                raise err.PathNotExistError(val)
            elif setting == 'templates' and not(self.is_valid_template(val)):
                raise err.InvalidTemplateError(val)
        self.config[setting][key] = val

    def set_setting_key_val(self,setting,key,val):
        '''set new value within setting dictionary'''
        if not(setting in self.config.keys()):
            raise err.InvalidSettingError(setting)
        if not(key in self.config[setting].keys()):
            raise err.InvalidSettingKeyError(setting,key)
        if setting == 'directories' and not(os.path.exists(val)):
            raise err.PathNotExistError(val)
        elif setting == 'templates' and not(self.is_valid_template(val)):
            raise err.InvalidTemplateError(val)
        self.config[setting][key] = val

    def remove_setting_key(self,setting,key):
        '''remove key from setting dictionary'''
        if not(setting in self.config.keys()):
            raise err.InvalidSettingError(setting)
        if 'required' in self.config[setting]['__metadata__'].keys():
            if key in self.config[setting]['__metadata__']['required']:
                raise err.RequiredKeyError(key)
        self.config[setting].pop(key,None)

    def set_setting_key_required(self,setting,key):
        '''within setting, set key as required in __metadata__'''
        if not(setting in self.config.keys()):
            raise err.InvalidSettingError(setting)
        if not('required' in self.config[setting]['__metadata__'].keys()):
            self.config[setting]['__metadata__']['required'] = []
        if key not in self.config[setting]['__metadata__']['required']:
            self.config[setting]['__metadata__']['required'].append(key)

    def set_setting_key_optional(self,setting,key):
        '''within setting dictionary, remove key from required in metadata'''
        if not(setting in self.config.keys()):
            raise err.InvalidSettingError(setting)
        if not('required' in self.config[setting]['__metadata__'].keys()):
            self.config[setting]['__metadata__']['required'] = []
        try:
            self.config[setting]['__metadata__']['required'].remove(key)
        except ValueError:
            pass

    def save_config(self,fpath=None):
        if fpath is None:
            fpath = self._configPath
        with open(fpath,'w') as fp:
            json.dump(self.config,fp,indent=2)
