# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''Common
'''

from typing import Any, Dict, List


def response_data(data: Dict[str, Dict[int, Dict[str, Any]]]):
    """StorCLI json output parser for respone data.

    Args:
        data (dict): formatted output data from command line

    Returns:
        dict: response data
    """
    return data['Controllers'][0]['Response Data']


def response_data_subkey(data: Dict[str, Dict[int, Dict[str,  Any]]], subset: List[str]):
    """StorCLI json output parser for respone data.
       Also, it returs the data filtered by the first key found from the subset list.

    Args:
        data (dict): formatted output data from command line
        subset (List[str]): list of keys to filter the data

    Returns:
        dict: response data
    """
    response = response_data(data)

    ret = {}

    for key in subset:
        if key in response:
            ret = response[key]
            break

    return ret


def response_property(data: Dict[str,  Any]):
    """StorCLI json output parser for property.

    Args:

        data (dict): formatted output data from command line

    Returns:
        dict: property data
    """
    return response_data(data)['Controller Properties']


def response_cmd(data: Dict[str, Dict[int, Dict[str,  Any]]]):
    """StorCLI json output parser for general cmd status.

    Args:
        data (dict): formatted output data from command line

    Returns:
        dict: cmd status
    """
    return data['Controllers'][0]['Command Status']


def response_setter(data: Dict[str, Dict[int, Dict[str,  Any]]]):
    """StorCLI json output parser for set cmd status.

    Args:
        data (dict): formatted output data from command line

    Returns:
        str: cmd detailed status value
    """
    if 'Controllers' in data:
        return data['Controllers'][0]['Command Status']
    else:
        return response_cmd(data)['Detailed Status'][0]['Value']


def lower(func):
    """Decorator to lower returned function string.

    Args:
        func (func): function

    Returns:
        str: lower output of func
    """
    def wrapper(*args, **kwargs):
        """func effective wrapper
        """
        return func(*args, **kwargs).lower()
    return wrapper


def upper(func):
    """Decorator to upper returned function string.

    Args:
        func (func): function

    Returns:
        str: upper output of func
    """
    def wrapper(*args, **kwargs):
        """func effective wrapper
        """
        return func(*args, **kwargs).upper()
    return wrapper


def strip(func):
    """Decorator to strip returned function string. It will be stripped both sides.

    Args:
        func (func): function

    Returns:
        str: stripped output of func
    """
    def wrapper(*args, **kwargs):
        """func effective wrapper
        """
        return func(*args, **kwargs).strip()
    return wrapper


def stringify(func):
    """Decorator to convert obj to string.

    Args:
        func (func): function

    Returns:
        str: lower output of func
    """
    def wrapper(*args, **kwargs):
        """func effective wrapper
        """
        return '{0}'.format(func(*args, **kwargs))
    return wrapper


def drives_from_expression(expr):
    """Generate list of drives from StorCLI drivers expression.

    Args:
        expr (str): drives string in StorCLI format (e:s|e:s-x|e:s-x,y;e:s-x,y,z)

    Returns:
        list: drives in format "enclosure:slot"
    """
    # Test cases:
    #   e:s
    #   e1:s,e2:s
    #   e:s,e:s
    #   e:x-y
    #   e:a-b,c-d
    #   e:a-b,z,c-d
    #   e1:a-b,z,c-d,e2:a-b,z,c-d

    def get_encl_id(pos=0):
        """Get enclosure id from expression
        """
        range_pos = expr[pos:].find(':')
        encl_id = expr[pos:range_pos]
        pos += range_pos + 1
        return (encl_id, pos)

    def get_nearest_separator():
        """Get nearest expression separator
        """
        types = {
            'slot': expr[pos:].find(',') % 1000,
            'range': expr[pos:].find('-') % 1000,
            'encl':  expr[pos:].find(':') % 1000,
            'end': len(expr[pos:]),
        }
        return sorted(list(types.items()), key=lambda x: x[1])[0]

    drives = []
    encl_id, pos = get_encl_id(0)

    while True:
        sep_t, sep_pos = get_nearest_separator()
        if sep_t == 'end':
            # end of expression
            drives.append('{0}:{1}'.format(encl_id, expr[pos:]))
            break
        if sep_t == 'slot':
            # slot
            drives.append("{0}:{1}".format(encl_id, expr[pos:pos+sep_pos]))
            pos += sep_pos + 1
        elif sep_t == 'range':
            # range
            range_start = expr[pos:pos+sep_pos]
            pos += sep_pos + 1

            range_sep_t, reange_sep_pos = get_nearest_separator()
            if range_sep_t == 'end':
                range_stop = len(expr[pos:])
            else:
                range_stop = reange_sep_pos

            range_end = expr[pos:pos+range_stop]
            pos += range_stop + 1

            for i in range(int(range_start), int(range_end)+1):
                drives.append("{0}:{1}".format(encl_id, i))

            if range_sep_t == 'end':
                break
        else:
            # enclosure
            drives.extend(drives_from_expression(expr[pos:]))
            break
    return drives


def expand_drive_ids(drives: str) -> str:
    """Expand drive ids to range if needed

    Args:
        drives (str): storcli drives expression (e:s|e:s-x|e:s-x,y;e:s-x,y,z)

    Returns:
        (str): expanded drives expression (without dashes)
    """
    drive_list = drives.split(',')
    output = ""

    for i, drive in enumerate(drive_list):
        drive = drive.strip()
        encl, slot = drive.split(':')
        new_output = drive

        encl = encl.strip()
        slot = slot.strip()

        if '-' in slot:
            begin, end = slot.split('-')

            begin = begin.strip()
            end = end.strip()

            new_output = ','.join(['{0}:{1}'.format(encl, i)
                                   for i in range(int(begin), int(end)+1)])

        if i > 0:
            output += ',' + new_output
        else:
            output += new_output

    return output


def count_drives(drives: str) -> int:
    """Count number of drives in drives expression

    Args:
        drives (str): storcli drives expression (e:s|e:s-x|e:s-x,y;e:s-x,y,z)

    Returns:
        (int): number of drives
    """

    expanded_drives = expand_drive_ids(drives)
    return len(expanded_drives.split(','))
