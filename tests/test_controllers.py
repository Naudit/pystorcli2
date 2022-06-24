# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

import json
import os
import pytest

from pystorcli import StorCLI

# discover tests

dataset_main_path = './tests/datatest/controllerSet/'

folders = [dataset_main_path +
           p for p in os.listdir(dataset_main_path)]


class TestSingleDevice():

    def get_device_data(self, folder: str):
        with open(os.path.join(folder, 'device.json')) as json_file:
            data = json.load(json_file)

        return data

    @pytest.mark.parametrize("folder", folders)
    def test_init_pystorcli(self, folder):
        try:
            storcli = StorCLI()
        except:
            pass
