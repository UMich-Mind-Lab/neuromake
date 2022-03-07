#!/bin/env python3
# PYTHON_ARGCOMPLETE_OK

######################### ARGPARSE/ARGCOMPLETE #################################
import argparse, argcomplete
import json

def get_possible_bids_vars(config):
    '''
    function reads config['bids_formats']['datatype_keys'] and the current
    config['bids'] to determine which variables can be added to config['bids'].
    This allows us to create a list of valid options for argument parsing

    :config: master sm_config.json file
    :return: list of bids variables
    '''
    x = []
    for k,v in config['bids_formats']['datatype_keys'].items():
        for i in v:
            if k != 'bids':
                i = f'{k}_{i}'
            if i not in config['bids'].keys():
                x.append(i)
    return x


if __name__ == "__main__":
    # read in config
    with open('config/sm_config.json','r') as fp:
        x = fp.read()
    config = json.loads(x)

    #parse arguments
    args = parse_args(config)

################################################################################



def print_dict(d):
    '''
    pretty prints the contents of dictionary, assuming dictionary is not nested
    and only contains values or lists. Used to give feedback to changes in config

    :d: input dictionary
    :return: None
    '''
    keys = sorted(d.keys())
    for k in keys:
        if isinstance(d[k],list):
            v = '\n\t'.join([ str(x) for x in d[k] ])
            print('{k}:\n\t{v}'.format(k=k,v=v))
        else:
            print('{k}:\n\t{v}'.format(k=k,v=d[k]))

def warning_check(msg):
    '''
    this function prompts the user to respond to a message with either 'Y' or 'N'
    to continue. It will reprompt the message until a valid message is supplied

    :msg: string to display to user
    :return: boolean True to continue, False to abort
    '''
    resp = None
    while resp is None:
        x = input(f'{msg} [Y/N]: ')
        if x.lower() in ['y','yes']:
            resp = True
        elif x.lower() in ['n','no']:
            resp = False
        else:
            print(f'{x} is not a valid response. Please respond with "Y" or "N"')
    return resp



def string2datatype(s,data_type):
    '''
    cast string to the appropriate type, if type is not specified (i.e., None),
    then we'll try to implicitly determine it in the following order:
    float > int > bool > str
    written for use in output of argparse, in cases where type must be dynamic

    :param s: unsanitized string
    :param data_type: specified data_type (None if not specified)
    :return: list cast to specified data type
    '''

    if data_type == 'bool':
            if s.lower() in ['t','true','1']:
                return True
            elif s.lower() in ['f','false','0']:
                return False
            else:
                raise Exception(f'Boolean type specified but {s} does not match any expected format (e.g., True, False, T, F, t, f, 1, 0)')
    elif data_type is not None:
        t = locate(data_type)
        return t(s)
    else:
        if multireplace(s,{'-':'','.':''}).isnumeric() and s.count('-') <= 1 and s.count('.') <= 1:
            if s.count('.') == 1:
                return float(s)
            else:
                return int(s)
        elif s.lower() in ['t','true','1']:
            return True
        elif s.lower() in ['f','false','0']:
            return False
        else:
            return s
    return out

def index_bids_db(config):
    print(f'[{time.strftime("%H:%M:%S")}]','Resetting indexed bids layout database...')
    layout = BIDSLayout(config['directories']['bids'],database_path=config['directories']['bidslayout'],reset_database=True)
    print(f'[{time.strftime("%H:%M:%S")}]','Done.')


def unique(mylist):
    '''
    return unique elements of mylist as list, preserving order of first occurrence
    '''
    x = []
    for i in mylist:
        if i not in x:
            x.append(i)
    return x




if __name__ == '__main__':
    #update config
    config = update_config(config,args)

    # reindex database if requested
    if args['reindex_db']:
        index_bids_db(config)

    # resave config file
    with open('config/sm_config.json','w') as fp:
        fp.write(json.dumps(config,indent=2))
