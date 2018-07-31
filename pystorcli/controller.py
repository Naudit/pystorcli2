# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI controller python module
'''

from . import StorCLI
from . import common
from . import enclosure
from . import virtualdrive
from . import exc


class ControllerMetrics(object):
    """StorCLI Controller Metrics

    Instance of this class represents controller metrics
    """
    def __init__(self, ctl):
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
        self._ctl = ctl

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
    @common.lower
    def state(self):
        """(str): controller status (Needs Attention | Optimal | Failed | Unknown)
        """
        return self._status["Controller Status"]

    @property
    def memory_correctable_error(self):
        """(str): number of controllers memory correctable errors
        """
        return self._status["Memory Correctable Errors"]

    @property
    def memory_uncorrectable_error(self):
        """(str): number of controllers memory uncorrectable errors
        """
        return self._status["Memory Uncorrectable Errors"]

    @property
    def drive_groups(self):
        """(str): number of drive groups on controller
        """
        data = self._show_all
        if 'Drive Groups' in data:
            return data["Drive Groups"]
        return str(0)

    @property
    def virtual_drives(self):
        """(str): number of virtual drives on controller
        """
        data = self._show_all
        if 'Virtual Drives' in data:
            return data["Virtual Drives"]
        return str(0)

    @property
    def virtual_drives_non_optimal(self):
        """(dict): number of virtual drives with in non optimal state
        """
        vds = {}

        if not self._ctl.vds.has_vds:
            return vds

        for vd in self._ctl.vds:
            if not vd.state == 'optimal':
                if vd.state in vds:
                    vds[vd.state] += 1
                else:
                    vds[vd.state] = 1
        return vds

    @property
    def physical_drives(self):
        """(str): number of physical drives on controller
        """
        data = self._show_all

        if 'Physical Drives' in data:
            return data["Physical Drives"]
        return str(0)

    @property
    def physical_drives_non_optimal(self):
        """(dict): number of physical drives in non optimal state (UBad | Offln)
        """
        drives = {}

        for encl in self._ctl.encls:
            if not encl.has_drives:
                continue
            for drive in encl.drives:
                if not drive.state in ('good', 'online'):
                    if drive.state in drives:
                        drives[drive.state] += 1
                    else:
                        drives[drive.state] = 1
        return drives

    @property
    def roc_temperature(self):
        """(str): RAID-on-Chip temperature or unknown if absent
        """
        hwcfg = self._hwcfg
        if hwcfg['Temperature Sensor for ROC'] == 'Present':
            return hwcfg['ROC temperature(Degree Celsius)']
        return 'unknown'

    @property
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


class Controller(object):
    """StorCLI Controller

    Instance of this class represents controller in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        id (str): controller id
        name (str): controller cmd name
        facts (dict): raw controller facts
        metrics (:obj:ControllerMetrics): controller metrics
        vds (list of :obj:virtualdrive.VirtualDrives): controller virtual drives
        encls (:obj:enclosure.Enclosures): controller enclosures

    Methods:
        create_vd (:obj:VirtualDrive): create virtual drive

    """
    def __init__(self, ctl_id, binary='storcli64'):
        """Constructor - create StorCLI Controller object

        Args:
            ctl_id (str): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}'.format(self._ctl_id)

        self._exist()

    def __str__(self):
        return '{0}'.format(common.response_data(self._run(['show'])))

    def _run(self, args, **kwargs):
        args = args[:]
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

    def _exist(self):
        try:
            self._run(['show'])
        except exc.StorCliCmdError:
            raise exc.StorCliMissingError(self.__class__.__name__, self._name)

    @property
    def id(self):
        """ (str): controller id
        """
        return self._ctl_id

    @property
    def name(self):
        """ (str): controller cmd name
        """
        return self._name

    @property
    def facts(self):
        """ (dict): raw controller facts
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """(:obj:ControllerMetrics): controller metrics
        """
        return ControllerMetrics(ctl=self)

    @property
    def vds(self):
        """(:obj:virtualdrive.VirtualDrives): controllers virtual drives
        """
        return virtualdrive.VirtualDrives(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def encls(self):
        """(:obj:enclosure.Enclosures): controller enclosures
        """
        return enclosure.Enclosures(ctl_id=self._ctl_id, binary=self._binary)

    def create_vd(self, name, raid, drives, strip='64'):
        """Create virtual drive (raid) managed by current controller

        Args:
            name (str): virtual drive name
            raid (str): virtual drive raid level (raid0, raid1, ...)
            drives (str): storcli drives expression (e:s|e:s-x|e:s-x,y;e:s-x,y,z)
            strip (str, optional): virtual drive raid strip size

        Returns:
            (None): no virtual drive created with name
            (:obj:virtualdrive.VirtualDrive)
        """
        args = [
            'add',
            'vd',
            'type={0}'.format(raid),
            'name={0}'.format(name),
            'drives={0}'.format(drives),
            'strip={0}'.format(strip)
        ]

        self._run(args)
        for vd in self.vds:
            if name == vd.name:
                return vd
        return None


class Controllers(object):
    """StorCLI Controllers

    Instance of this class is iterable with :obj:Controller as item

    Args:
        binary (str): storcli binary or full path to the binary

    Properties:
        ids (list of str): list of controllers id

    Methods:
        get_clt (:obj:Controller): return controller object by id
    """
    def __init__(self, binary='storcli64'):
        """Constructor - create StorCLI Controllers object

        Args:
            binary (str): storcli binary or full path to the binary
        """
        self._binary = binary
        self._storcli = StorCLI(binary)

    @property
    def _ctl_ids(self):
        out = self._storcli.run(['show'])
        return [ctl['Ctl'] for ctl in common.response_data(out)['System Overview']]

    @property
    def _ctls(self):
        for ctl_id in self._ctl_ids:
            yield Controller(ctl_id=ctl_id, binary=self._binary)

    def __iter__(self):
        return self._ctls

    @property
    def ids(self):
        """(list of str): controllers id
        """
        return self._ctl_ids

    def get_ctl(self, ctl_id):
        """Get controller object by id

        Args:
            ctl_id (str): controller id

        Returns:
            (None): no controller with id
            (:obj:Controller): controller object
        """
        for ctl in self:
            if ctl.id == ctl_id:
                return ctl
        return None
