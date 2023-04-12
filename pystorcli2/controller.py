# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI controller python module
'''

from . import StorCLI
from . import common
from . import enclosure
from . import drive
from . import virtualdrive
from . import exc

from typing import List, Optional, Union


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
        vds = {}

        if not self._ctl.vds.has_vds:
            return vds

        for vd in self._ctl.vds:
            if not vd.state == 'optimal':
                if vd.state in vds:
                    vds[vd.state] += 1
                else:
                    vds[vd.state] = 1

        # convert counter to string
        return {k: str(v) for k, v in vds.items()}

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
        drives = {}

        for encl in self._ctl.encls:
            if not encl.has_drives:
                continue
            for drive in encl.drives:
                if not drive.state in ('good', 'online', 'ghs', 'dhs'):
                    if drive.state in drives:
                        drives[drive.state] += 1
                    else:
                        drives[drive.state] = 1

        # convert counter to string
        return {k: str(v) for k, v in drives.items()}

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
        autorebuild (dict): current auto rebuild state (also setter)
        foreignautoimport (dict): imports foreign configuration automatically at boot (also setter)
        patrolread (dict): current patrol read settings (also setter)

    Methods:
        create_vd (:obj:VirtualDrive): create virtual drive
        set_patrolread (dict): configures patrol read state and schedule
        patrolread_start (dict): starts a patrol read on controller
        patrolread_pause (dict): pauses patrol read on controller
        patrolread_resume (dict): resumes patrol read on controller
        patrolread_stop (dict): stops patrol read if running on controller
        patrolread_running (bool): check if patrol read is running on controller

    TODO:
        Implement missing methods:
            * patrol read progress
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
            raise exc.StorCliMissingError(
                self.__class__.__name__, self._name) from None

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

    @property
    def drives_ids(self) -> List[str]:
        """(list of str): list of drives ids in format (e:s)
        """
        drives = []
        for encl in self.encls:
            for id in encl.drives.ids:
                drives.append("{enc}:{id}".format(enc=encl.id, id=id))

        return drives

    def create_vd(self, name: str, raid: str, drives: str, strip: str = '64', PDperArray: Optional[int] = None) -> Optional[virtualdrive.VirtualDrive]:
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
            'r{0}'.format(raid),
            'name={0}'.format(name),
            'drives={0}'.format(drives),
            'strip={0}'.format(strip)
        ]

        try:
            if int(raid) >= 10 and PDperArray is None:
                # Try to count the number of drives in the array
                # The format of the drives argument is e:s|e:s-x|e:s-x,y;e:s-x,y,z

                numDrives = common.count_drives(drives)

                if numDrives % 2 != 0 and numDrives % 3 == 0:
                    # In some scenarios, such as 9 drives with raid 60, 3 is a good pd number but 4 is not
                    # Must check for similar scenarios
                    # BTW we don't clearly understand what PDperArray is for and what exactly it does under the hood. More investigation is needed
                    PDperArray = numDrives//3
                else:
                    PDperArray = numDrives//2

        except ValueError:
            pass

        finally:
            if raid == '00' and PDperArray is None:
                PDperArray = 1

        if PDperArray is not None:
            args.append('PDperArray={0}'.format(PDperArray))

        self._run(args)
        for vd in self.vds:
            if name == vd.name:
                return vd
        return None

    @property
    @common.lower
    def autorebuild(self):
        """Get/Set auto rebuild state

        One of the following options can be set (str):
            on - enables autorebuild
            off - disables autorebuild

        Returns:
            (str): on / off
        """
        args = [
            'show',
            'autorebuild'
        ]

        prop = common.response_property(self._run(args))[0]
        return prop['Value']

    @autorebuild.setter
    def autorebuild(self, value):
        """
        """
        args = [
            'set',
            'autorebuild={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    @common.lower
    def foreignautoimport(self):
        """Get/Set auto foreign import configuration

        One of the following options can be set (str):
            on - enables foreignautoimport
            off - disables foreignautoimport

        Returns:
            (str): on / off
        """
        args = [
            'show',
            'foreignautoimport'
        ]
        prop = common.response_property(self._run(args))[0]
        return prop['Value']

    @foreignautoimport.setter
    def foreignautoimport(self, value):
        """
        """
        args = [
            'set',
            'foreignautoimport={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    @common.lower
    def patrolread(self):
        """Get/Set patrol read

        One of the following options can be set (str):
            on - enables patrol read
            off - disables patrol read

        Returns:
            (str): on / off
        """
        args = [
            'show',
            'patrolread'
        ]

        for pr in common.response_property(self._run(args)):
            if pr['Ctrl_Prop'] == "PR Mode":
                if pr['Value'] == 'Disable':
                    return 'off'
                else:
                    return 'on'
        return 'off'


    @patrolread.setter
    def patrolread(self, value):
        """
        """
        return self.set_patrolread(value)


    def set_patrolread(self, value, mode='manual'):
        """Set patrol read

        Args:
            value (str): on / off to configure patrol read state
            mode (str): auto | manual to configure patrol read schedule
        """
        args = [
            'set',
            'patrolread={0}'.format(value)
        ]

        if value == 'on':
            args.append('mode={0}'.format(mode))

        return common.response_setter(self._run(args))

    def patrolread_start(self):
        """Starts the patrol read operation of the controller

        Returns:
            (dict): response cmd data
        """
        args = [
            'start',
            'patrolread'
        ]
        return common.response_cmd(self._run(args))

    def patrolread_stop(self):
        """Stops the patrol read operation of the controller

        Returns:
            (dict): response cmd data
        """
        args = [
            'stop',
            'patrolread'
        ]
        return common.response_cmd(self._run(args))

    def patrolread_pause(self):
        """Pauses the patrol read operation of the controller

        Returns:
            (dict): response cmd data
        """
        args = [
            'pause',
            'patrolread'
        ]
        return common.response_cmd(self._run(args))

    def patrolread_resume(self):
        """Resumes the patrol read operation of the controller

        Returns:
            (dict): response cmd data
        """
        args = [
            'resume',
            'patrolread'
        ]
        return common.response_cmd(self._run(args))

    @property
    def patrolread_running(self):
        """Check if patrol read is running on the controller

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'patrolread'
        ]

        status = ''
        for pr in common.response_property(self._run(args)):
            if pr['Ctrl_Prop'] == "PR Current State":
                status = pr['Value']
        return bool('Active' in status)


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

    @ property
    def _ctl_ids(self) -> List[str]:
        out = self._storcli.run(['show'])
        response = common.response_data(out)

        if "Number of Controllers" in response and response["Number of Controllers"] == 0:
            return []
        else:
            return [ctl['Ctl'] for ctl in common.response_data_subkey(out, ['System Overview', 'IT System Overview'])]

    @ property
    def _ctls(self):
        for ctl_id in self._ctl_ids:
            yield Controller(ctl_id=ctl_id, binary=self._binary)

    def __iter__(self):
        return self._ctls

    @ property
    def ids(self):
        """(list of str): controllers id
        """
        return self._ctl_ids

    def get_ctl(self, ctl_id: int) -> Optional[Controller]:
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
