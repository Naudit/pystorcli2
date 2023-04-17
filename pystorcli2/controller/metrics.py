# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI controller python module
'''

import pystorcli2
from .. import common
from ..drive.state import DriveState

from typing import Dict


class ControllerMetrics(object):
    """StorCLI Controller Metrics

    Instance of this class represents controller metrics
    """

    def __init__(self, ctl: 'pystorcli2.controller.Controller'):
        """Constructor - create StorCLI ControllerMetrics object

        Args:
            ctl (:obj:Controller): controller object

        Properties:
            state (str): controller status
            memory_correctable_error (str): number of controllers memory correctable errors
            memory_uncorrectable_error (str): number of controllers memory uncorrectable errors
            drive_groups (str): number of drive groups on controller
            virtual_drives (str): number of virtual drives on controller
            virtual_drives_non_optimal (dict): number of virtual drives with in non optimal state
            physical_drives (str): number of physical drives on controller
            physical_drives_non_optimal (dict): number of physical drives in non optimal state
            roc_temperature (str): RAID-on-Chip temperature
            ctl_temperature (str): controller temperature
            all (dict): all metrics
        """
        self._ctl: 'pystorcli2.controller.Controller' = ctl

    @property
    def _show_all(self):
        args = [
            'show',
            'all',
        ]
        return common.response_data(self._ctl._run(args))

    @property
    def _status(self):
        return self._show_all['Status']

    @property
    def _hwcfg(self):
        return self._show_all['HwCfg']

    @property
    @common.stringify
    @common.lower
    def state(self):
        """(str): controller status (Needs Attention | Optimal | Failed | Unknown)
        """
        return self._status["Controller Status"]

    @property
    @common.stringify
    def memory_correctable_error(self):
        """(str): number of controllers memory correctable errors
        """
        return self._status["Memory Correctable Errors"]

    @property
    @common.stringify
    def memory_uncorrectable_error(self):
        """(str): number of controllers memory uncorrectable errors
        """
        return self._status["Memory Uncorrectable Errors"]

    @property
    @common.stringify
    def drive_groups(self):
        """(str): number of drive groups on controller
        """
        data = self._show_all
        if 'Drive Groups' in data:
            return data["Drive Groups"]
        return 0

    @property
    @common.stringify
    def virtual_drives(self):
        """(str): number of virtual drives on controller
        """
        data = self._show_all
        if 'Virtual Drives' in data:
            return data["Virtual Drives"]
        return 0

    @property
    def virtual_drives_non_optimal(self):
        """(dict): number of virtual drives with in non optimal state
        """
        vds: Dict[str, int] = {}

        if not self._ctl.vds.has_vds:
            return vds

        for vd in self._ctl.vds:
            if not vd.state == 'optimal':
                if vd.state in vds:
                    vds[vd.state] += 1
                else:
                    vds[vd.state] = 1

        # convert counter to string
        return {str(k): str(v) for k, v in vds.items()}

    @property
    @common.stringify
    def physical_drives(self):
        """(str): number of physical drives on controller
        """
        data = self._show_all

        if 'Physical Drives' in data:
            return data["Physical Drives"]
        return 0

    @property
    def physical_drives_non_optimal(self):
        """(dict): number of physical drives in non optimal state (UBad | Offln)
        """
        drives: Dict[DriveState, int] = {}

        for encl in self._ctl.encls:
            if not encl.has_drives:
                continue
            for drive in encl.drives:
                if not drive.state.is_good():
                    if drive.state in drives:
                        drives[drive.state] += 1
                    else:
                        drives[drive.state] = 1

        # convert counter to string
        return {str(k): str(v) for k, v in drives.items()}

    @property
    @common.stringify
    def roc_temperature(self):
        """(str): RAID-on-Chip temperature or unknown if absent
        """
        hwcfg = self._hwcfg
        if hwcfg['Temperature Sensor for ROC'] == 'Present':
            return hwcfg['ROC temperature(Degree Celsius)']
        return 'unknown'

    @property
    @common.stringify
    def ctl_temperature(self):
        """(str): Controller temperature or unknown if absent
        """
        hwcfg = self._hwcfg

        if hwcfg['Temperature Sensor for Controller'] == 'Present':
            return hwcfg['Controller temperature(Degree Celsius)']
        return 'unknown'

    @property
    def all(self):
        """(dict): all metrics
        """
        metrics = {}

        for attribute in dir(self):
            if not attribute.startswith('_') and not attribute == 'all':
                metrics[attribute] = self.__getattribute__(attribute)
        return metrics
