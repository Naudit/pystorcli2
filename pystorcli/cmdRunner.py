# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''CMDRunner
'''

import subprocess


class CMDRunner():
    """This is a simple wrapper for subprocess.Popen()/subprocess.run(). The main idea is to inherit this class and create easy mockable tests.
    """

    def run(self, args, **kwargs):
        """Runs a command and returns the output.
        """
        return subprocess.run(args, **kwargs)
