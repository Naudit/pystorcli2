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

from pystorcli2 import common


class TestCommonFuncs():

    def test_expand_drive_ids(self):
        assert common.expand_drive_ids(
            '0:0') == '0:0'
        assert common.expand_drive_ids(
            '0:0-1') == '0:0,0:1'
        assert common.expand_drive_ids(
            '0:0-2') == '0:0,0:1,0:2'
        assert common.expand_drive_ids(
            '0:0-1,0:3-4') == '0:0,0:1,0:3,0:4'
        assert common.expand_drive_ids(
            '0:0-1,0:3-4,1:0-1') == '0:0,0:1,0:3,0:4,1:0,1:1'
        assert common.expand_drive_ids(
            '0:0-1,0:3-4,1:0-1,5:3-4') == '0:0,0:1,0:3,0:4,1:0,1:1,5:3,5:4'
        assert common.expand_drive_ids(
            '0:0-1 ,0:3-4, 1:0-1 , 5 : 3 - 4  ') == '0:0,0:1,0:3,0:4,1:0,1:1,5:3,5:4'
        assert common.expand_drive_ids(
            '177:18,177:19,177:20,177:21,177:22,177:23') == '177:18,177:19,177:20,177:21,177:22,177:23'

    def test_count_drives(self):
        assert common.count_drives(
            '0:0') == 1
        assert common.count_drives(
            '0:0-1') == 2
        assert common.count_drives(
            '0:0-2') == 3
        assert common.count_drives(
            '0:0-1,0:3-4') == 4
        assert common.count_drives(
            '0:0-1,0:3-4,1:0-1') == 6
        assert common.count_drives(
            '0:0-1,0:3-4,1:0-1,5:3-4') == 8
        assert common.count_drives(
            '0:0-1 ,0:3-4, 1:0-1 , 5 : 3 - 4  ') == 8
        assert common.count_drives(
            '177:18,177:19,177:20,177:21,177:22,177:23') == 6
