# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

import json
import os
from typing import List
from pystorcli2 import StorCLI
from .storclifile import StorcliCMDFile


class TestStorcliMainClass():

    def get_device_data(self, folder: str):
        with open(os.path.join(folder, 'device.json')) as json_file:
            data = json.load(json_file)

        return data

    def get_cmdRunner(self, folder: str, options: List[str] = []):
        return StorcliCMDFile(folder, options)

    def setupEnv(self, folder: str):
        # Check if storcli exists in self
        if hasattr(self, 'storcli'):
            return

        # get cmdRunner
        cmdRunner = self.get_cmdRunner(folder)

        StorCLI.enable_singleton()
        self.storcli = StorCLI(cmdrunner=cmdRunner)
        self.storcli.clear_cache()
        # Conflirm cmdRunner is set properly
        self.storcli.set_cmdrunner(cmdRunner)

        return self.get_device_data(folder)

    def get_storcli(self, folder: str):
        self.setupEnv(folder)

        return self.storcli
