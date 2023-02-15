# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''CMDRunner
'''

import os
import shutil
import subprocess
from . import exc


class CMDRunner():
    """This is a simple wrapper for subprocess.Popen()/subprocess.run(). The main idea is to inherit this class and create easy mockable tests.
    """

    def run(self, args, **kwargs) -> subprocess.CompletedProcess:
        """Runs a command and returns the output.
        """
        return subprocess.run(args, **kwargs)

    def binaryCheck(self, binary):
        """Verify and return full binary path
        """
        _bin = shutil.which(binary)
        if not _bin:
            raise exc.StorCliError(
                "Cannot find storcli binary '%s' in path: %s" % (binary, os.environ['PATH']))
        return _bin
