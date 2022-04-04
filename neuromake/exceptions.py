class WildcardValueError(Exception):
    '''value error with wildcard object'''

class WildcardTypeError(Exception):
    '''type error with wildcard object'''

class WildcardRequiredError(Exception):
    '''errors related to required wildcard'''

class WildcardNotIterableError(Exception):
    '''errors related to iterability of wildcard'''

class AppConfigError(Exception):
    '''errors related to app config file'''
    
class PathNotExistError(Exception):
    '''Exception raised for errors in filepaths'''
    def __init__(self,fp):
        self.message = f'"{fp}" does not exist'
        super().__init__(self.message)

class InvalidMenuError(Exception):
    '''Exception raised for invalid menu in config'''
    def __init__(self,menu):
        self.message = f'config["{menu}"] does not exist.'
        super().__init__(self.message)

class RequiredMenuLabelError(Exception):
    '''Exception raised if label is required but not present'''

class InvalidMenuLabelError(Exception):
    '''Exception raised for invalid label for config[menu][label]'''
    def __init__(self,menu,label,valid=None):
        self.message = f'"{label}" is not a valid label for {menu}.'
        if valid is not None:
            self.message += f' Must be one of {valid}.'
        super().__init__(self.message)

class InvalidTemplateError(Exception):
    '''Exception raised if value for config['templates'][label] is invalid'''
    def __init__(self,template,valid=None):
        self.message = f'"{template}" is not a valid template.'
        if valid is not None:
            self.message += f' Must only include fieldnames in list: {valid}'
        super().__init__(self.message)

class KeyNotDefinedError(Exception):
    '''exception raised if key isn't defined within dict'''
