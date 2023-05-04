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

from pystorcli2 import StorCLI
from pystorcli2 import Controller, Controllers
from .baseTest import TestStorcliMainClass

# discover tests

dataset_main_path = './tests/datatest/controllerSet/'

folders = [dataset_main_path +
           p for p in os.listdir(dataset_main_path)]


class TestControllers(TestStorcliMainClass):

    @pytest.mark.parametrize("folder", folders)
    def test_count_controllers(self, folder):
        # setup env
        device_data = self.setupEnv(folder)

        # List controllers
        controllers = Controllers()

        assert device_data
        if "Controller_ids" in device_data:
            assert controllers.ids == device_data["Controller_ids"]

    @pytest.mark.parametrize("folder", folders)
    def test_get_controller(self, folder):
        # setup env
        device_data = self.setupEnv(folder)

        # List controllers
        controllers = Controllers()

        assert device_data
        if "Controller_ids" in device_data and len(controllers.ids) > 0:
            assert controllers.get_ctl(controllers.ids.pop())
