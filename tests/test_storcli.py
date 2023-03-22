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
from .baseTest import TestStorcliMainClass


# discover tests
dataset_main_path = './tests/datatest/storcliSet/'

folders = [dataset_main_path +
           p for p in os.listdir(dataset_main_path)]


class TestStorcli(TestStorcliMainClass):

    @pytest.mark.parametrize("folder", folders)
    def test_init_disable_singleton(self, folder):
        # get cmdRunner
        cmdRunner = self.get_cmdRunner(folder)

        StorCLI.disable_singleton()
        storcli = StorCLI(cmdrunner=cmdRunner)

        assert not StorCLI.is_singleton()

    @pytest.mark.parametrize("folder", folders)
    def test_init_enable_singleton(self, folder):
        # get cmdRunner
        cmdRunner = self.get_cmdRunner(folder)

        StorCLI.enable_singleton()
        storcli = StorCLI(cmdrunner=cmdRunner)

        assert StorCLI.is_singleton()

    @pytest.mark.parametrize("folder", folders)
    def test_init_valid_exec(self, folder):
        storcli = StorCLI(binary='sh')

    @pytest.mark.parametrize("folder", folders)
    def test_init_invalid_exec(self, folder):
        from pystorcli2.exc import StorCliError

        StorCLI.disable_singleton()

        with pytest.raises(StorCliError):
            storcli = StorCLI(binary='idontexist')
