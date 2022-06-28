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
from pystorcli import StorCLI
from .storclifile import StorcliCMDFile


class TestStorcliMainClass():

    def get_device_data(self, folder: str):
        with open(os.path.join(folder, 'device.json')) as json_file:
            data = json.load(json_file)

        return data

    def get_cmdRunner(self, folder: str, options: List[str] = []):
        return StorcliCMDFile(folder, options)

    def setupEnv(self, folder: str):
        # get cmdRunner
        cmdRunner = self.get_cmdRunner(folder)

        StorCLI.enable_singleton()
        r = StorCLI(cmdrunner=cmdRunner)

        return self.get_device_data(folder)
