# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################


import re
import os
import json
from pystorcli2.cmdRunner import CMDRunner, StorcliRet
from pystorcli2.errors import StorcliErrorCode
from .exceptions import StorclifileSampleNotFound
from typing import Union, Tuple, List

import logging
logger = logging.getLogger('pystorcli')


class StorcliCMDFile(CMDRunner):
    """This class is just a mockup of the CMDRunner class
    """

    def __init__(self, storcli_path, options: List[str] = []):
        """Instantiates and initializes the storcli wrapper."""

        self.storcli_path = storcli_path
        self.options: List[str] = options

    def run(self, args, pass_options=False, **kwargs) -> StorcliRet:
        """Runs a command and returns the output.
        """

        if pass_options:
            final_params = self.options + args[1:]
        else:
            final_params = args[1:]

        filename = '_' + '_'.join(final_params)

        filename = os.path.join(
            self.storcli_path, re.sub('[/\\\\:]', '_', filename))

        filename = filename+'.json'

        logger.debug("Opening file: {0}".format(filename))

        try:
            with open(filename) as f:
                raw_data = f.read()
        except:
            raise StorclifileSampleNotFound(filename, final_params)

        _stdout = raw_data

        retcode = 0

        # Try to infere the return code from the output
        try:
            _stdout_json = json.loads(_stdout)
            if 'Controllers' in _stdout_json:
                for cont_json in _stdout_json['Controllers']:
                    if 'Command Status' in cont_json:
                        # Check if the command status is not OK
                        if cont_json['Command Status']['Status'] != 'Success':
                            # If Detailed Status, obtain the return code
                            if 'Detailed Status' in cont_json['Command Status']:
                                retcode = cont_json['Command Status']['Detailed Status'][0]['ErrCd']
                            else:
                                # Otherwise, try to infere from the Description String
                                _code_type = StorcliErrorCode.get(
                                    cont_json['Command Status']['Description'])
                                retcode = _code_type.value
        except:
            pass

        ret = StorcliRet(_stdout, '', retcode)

        return ret

    def binaryCheck(self, binary):
        """Verify and return full binary path
        """

        return '/dev/null'
