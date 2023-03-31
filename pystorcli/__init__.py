# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI python module version 1.x (deprecated) I will keep it for compatibility with old code. It will load pystorcli2 module.
'''

import pystorcli2
from pystorcli2 import *
from pystorcli2.version import __version__

__all__ = ['__version__', 'StorCLI', 'Controller', 'Controllers',
           'Enclosure', 'Enclosures', 'Drive', 'Drives', 'VirtualDrive', 'VirtualDrives']
