class PathNotExistError(Exception):
    '''Exception raised for errors in filepaths'''
    def __init__(self,fp):
        self.message = f'"{fp}" does not exist'
        super().__init__(self.message)

class InvalidSettingError(Exception):
    '''Exception raised for invalid setting in config'''
    def __init__(self,setting):
        self.message = f'config["{setting}"] does not exist.'
        super().__init__(self.message)

class InvalidSettingKeyError(Exception):
    '''Exception raised for invalid key for config[setting][key]'''
    def __init__(self,setting,key,valid=None):
        self.message = f'"{key}" is an invalid key for config["{setting}"].'
        if valid is not None:
            self.message += f' Must be one of {valid}.'
        super().__init__(self.message)

class InvalidTemplateError(Exception):
    '''Exception raised if value for config['templates'][key] is invalid'''
    def __init__(self,template,valid=None):
        self.message = f'"{template}" is not a valid template.'
        if valid is not None:
            self.message += f' Must only include fieldnames in list: {valid}'
        super().__init__(self.message)

class RequiredKeyError(Exception):
    '''Exception raised if key in config['templates'] is required, but removal
    is attempted, or it otherwise doesn't exist'''
    def __init__(self,key):
        self.message = f'"{key}" is a required key.'
        super().__init__(self.message)
