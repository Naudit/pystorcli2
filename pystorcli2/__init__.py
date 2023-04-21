# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI python module version 2.x
'''

from .version import __version__
from .storcli import StorCLI
from .controller import Controller, Controllers
from .enclosure import Enclosure, Enclosures
from .drive import DriveState, Drive, Drives
from .virtualdrive import VirtualDrive, VirtualDrives

__all__ = ['__version__', 'StorCLI', 'Controller', 'Controllers',
           'Enclosure', 'Enclosures', 'DriveState', 'Drive', 'Drives', 'VirtualDrive', 'VirtualDrives']
