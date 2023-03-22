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
from typing import List

from pystorcli2 import StorCLI, Controllers, Controller, VirtualDrives, VirtualDrive
from .baseTest import TestStorcliMainClass


# discover tests
dataset_main_path = './tests/datatest/namedSet/'


def getTests(base_name: str) -> List[str]:
    """Gets the list of tests for a given base name

    Searchs in dataset_main_path for files with the given base name.
    """
    return [dataset_main_path + p for p in os.listdir(dataset_main_path) if p.startswith(base_name)]


class TestStorcliOperations(TestStorcliMainClass):

    @pytest.mark.parametrize("folder", getTests('create_vd_raid0'))
    def test_create_vd_raid0(self, folder):
        # get storcli
        s: StorCLI = self.get_storcli(folder)

        # get controller 0
        cs: Controllers = s.controllers
        c = cs.get_ctl(0)
        assert c is not None

        # create a new VD
        vd = c.create_vd('create_vd_raid0', '0', '35:12-13', '512')
        assert vd is not None

    @pytest.mark.parametrize("folder", getTests('delete_vd'))
    def test_delete_vd(self, folder):
        # get storcli
        s: StorCLI = self.get_storcli(folder)

        # get controller 0
        cs: Controllers = s.controllers
        c = cs.get_ctl(0)
        assert c is not None

        # get the vd
        vd = c.vds.get_vd('1')
        assert vd is not None

        # delete the vd
        assert vd.delete()['Status'] == 'Success'

    @pytest.mark.parametrize("folder", getTests('create_vd_raid1'))
    def test_create_vd_raid1(self, folder):
        # get storcli
        s: StorCLI = self.get_storcli(folder)
        # get controller 0
        cs: Controllers = s.controllers
        c = cs.get_ctl(0)
        assert c is not None
        # create a new VD
        vd = c.create_vd('create_vd_raid1', '1', '35:12-13', '512')
        assert vd is not None
