# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################


import re
import os
import subprocess
from pystorcli.cmdRunner import CMDRunner
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

    def run(self, args, pass_options=False, **kwargs) -> subprocess.CompletedProcess:
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

        ret = subprocess.CompletedProcess(args, 0, _stdout, None)

        return ret

    def binaryCheck(self, binary):
        """Verify and return full binary path
        """

        return '/dev/null'
