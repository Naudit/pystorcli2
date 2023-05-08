# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI controller python module
'''

from .. import StorCLI
from .. import common
from .. import enclosure
from .. import virtualdrive
from .. import exc
from ..errors import StorcliError

from datetime import datetime
from typing import List, Optional

# include submodules
from .metrics import ControllerMetrics


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
        cc (dict): current patrol read settings (also setter)
        has_foreign_configurations (bool): true if controller has foreign configurations

    Methods:
        create_vd (:obj:VirtualDrive): create virtual drive
        set_patrolread (dict): configures patrol read state and schedule
        patrolread_start (dict): starts a patrol read on controller
        patrolread_pause (dict): pauses patrol read on controller
        patrolread_resume (dict): resumes patrol read on controller
        patrolread_stop (dict): stops patrol read if running on controller
        patrolread_running (bool): check if patrol read is running on controller
        set_cc (dict): configures consistency check mode and start time
        import_foreign_configurations (dict): imports the foreign configurations on controller
        delete_foreign_configurations (dict): deletes the foreign configuration on controller

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

    def _run(self, args, allow_error_codes=[StorcliError.INCOMPLETE_FOREIGN_CONFIGURATION], **kwargs):
        args = args[:]
        args.insert(0, self._name)
        return self._storcli.run(args, allow_error_codes=allow_error_codes, **kwargs)

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

    @property
    @common.lower
    def cc(self):
        """Get/Set consistency chceck

        One of the following options can be set (str):
            seq  - sequential mode
            conc - concurrent mode
            off  - disables consistency check

        Returns:
            (str): on / off
        """
        args = [
            'show',
            'cc'
        ]

        for pr in common.response_property(self._run(args)):
            if pr['Ctrl_Prop'] == "CC Operation Mode":
                if pr['Value'] == 'Disabled':
                    return 'off'
                else:
                    return 'on'
        return 'off'

    @cc.setter
    def cc(self, value):
        """
        """
        return self.set_cc(value)

    def set_cc(self, value, starttime=None):
        """Set consistency check

        Args:
            value (str):
                seq  - sequential mode
                conc - concurrent mode
                off  - disables consistency check
            starttime (str): Start time of a consistency check is yyyy/mm/dd hh format
        """
        args = [
            'set',
            'cc={0}'.format(value)
        ]

        if value in ('seq', 'conc'):
            if starttime is None:
                starttime = datetime.now().strftime('%Y/%m/%d %H')
            args.append('starttime="{0}"'.format(starttime))

        return common.response_setter(self._run(args))

    def has_foreign_configurations(self, securitykey: Optional[str] = None) -> bool:
        """(bool): true if controller has foreign configurations
        """
        args = [
            '/fall',
            'show'
        ]

        if securitykey:
            args.append(f'securitykey={securitykey}')

        try:
            fc_data = common.response_data(self._run(args))
            fcs = 0

            if 'Total foreign Drive Groups' in fc_data:
                fcs = int(fc_data['Total foreign Drive Groups'])
            if 'Total Foreign PDs' in fc_data:
                fcs += int(fc_data['Total Foreign PDs'])
            if 'Total Locked Foreign PDs' in fc_data:
                fcs += int(fc_data['Total Locked Foreign PDs'])

            if fcs > 0:
                return True
        except KeyError:
            pass
        return False

    def is_foreign_configuration_healthy(self, securitykey: Optional[str] = None) -> bool:
        """(bool): true if controller has healthy foreign configurations
        """

        if not self.has_foreign_configurations(securitykey):
            return True

        args = [
            '/fall',
            'show'
        ]

        if securitykey:
            args.append(f'securitykey={securitykey}')

        try:
            fc_data = common.response_data(
                self._run(args, allow_error_codes=[]))
        except exc.StorCliCmdErrorCode as e:
            if e.error_code == StorcliError.INCOMPLETE_FOREIGN_CONFIGURATION:
                return False

            raise e

        return True

    def delete_foreign_configurations(self, securitykey: Optional[str] = None):
        """Deletes foreign configurations

        Returns:
            (dict): response cmd data
        """
        args = [
            '/fall',
            'del'
        ]

        if securitykey:
            args.append(f'securitykey={securitykey}')
        return common.response_cmd(self._run(args))

    def import_foreign_configurations(self, securitykey: Optional[str] = None):
        """Imports foreign configurations

        Returns:
            (dict): response cmd data
        """
        args = [
            '/fall',
            'import'
        ]
        if securitykey:
            args.append(f'securitykey={securitykey}')
        return common.response_cmd(self._run(args))


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
    def _ctl_ids(self) -> List[int]:
        out = self._storcli.run(['show'], allow_error_codes=[
            StorcliError.INCOMPLETE_FOREIGN_CONFIGURATION])
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
