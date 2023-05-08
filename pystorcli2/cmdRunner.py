# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''CMDRunner
'''

import os
import shutil
from subprocess import Popen, PIPE
from . import exc
from typing import List, Tuple


class StorcliRet():
    def __init__(self, stdout: str, stderr: str, returncode: int):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class CMDRunner():
    """This is a simple wrapper for subprocess.Popen()/subprocess.run(). The main idea is to inherit this class and create easy mockable tests.
    """

    def run(self, args, **kwargs) -> StorcliRet:
        """Runs a command and returns the output.
        """
        proc = Popen(args, stdout=PIPE, stderr=PIPE, **kwargs)

        _stdout, _stderr = [i for i in proc.communicate()]

        return StorcliRet(_stdout, _stderr, proc.returncode)

    def binaryCheck(self, binary) -> str:
        """Verify and return full binary path
        """
        _bin = shutil.which(binary)
        if not _bin:
            raise exc.StorCliError(
                "Cannot find storcli binary '%s' in path: %s" % (binary, os.environ['PATH']))
        return _bin
