# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI drive python module
'''

from . import StorCLI
from . import common
from . import controller
from . import enclosure
from . import virtualdrive
from . import exc

from typing import Union, List, Optional
from enum import Enum


class DriveState(Enum):
    """Drive status
    """
    # From storcli 7.1704
    # EID=Enclosure Device ID|Slt=Slot No|DID=Device ID|DG=DriveGroup
    # DHS=Dedicated Hot Spare|UGood=Unconfigured Good|GHS=Global Hotspare
    # UBad=Unconfigured Bad|Sntze=Sanitize|Onln=Online|Offln=Offline|Intf=Interface
    # Med=Media Type|SED=Self Encryptive Drive|PI=Protection Info
    # SeSz=Sector Size|Sp=Spun|U=Up|D=Down|T=Transition|F=Foreign
    # UGUnsp=UGood Unsupported|UGShld=UGood shielded|HSPShld=Hotspare shielded
    # CFShld=Configured shielded|Cpybck=CopyBack|CBShld=Copyback Shielded
    # UBUnsp=UBad Unsupported|Rbld=Rebuild

    DHS = 'Dedicated Hot Spare'
    UGood = 'Unconfigured Good'
    GHS = 'Global Hotspare'
    UBad = 'Unconfigured Bad'
    Sntze = 'Sanitize'
    Onln = 'Online'
    Offln = 'Offline'
    Failed = 'Failed'
    SED = 'Self Encryptive Drive'
    UGUnsp = 'UGood Unsupported'
    UGShld = 'UGood shielded'
    HSPShld = 'Hotspare shielded'
    CFShld = 'Configured shielded'
    Cpybck = 'CopyBack'
    CBShld = 'Copyback Shielded'
    UBUnsp = 'UBad Unsupported'
    Rbld = 'Rebuild'
    Missing = 'Missing'
    JBOD = 'JBOD'

    def __str__(self) -> str:
        return self.value

    def is_good(self) -> bool:
        """Check if drive is good according to status"""
        good_states = [
            DriveState.DHS,
            DriveState.UGood,
            DriveState.GHS,
            # DriveState.Sntze, ??
            DriveState.Onln,
            DriveState.SED,
            # DriveState.UGUnsp, ??
            DriveState.UGShld,
            DriveState.HSPShld,
            DriveState.CFShld,
            DriveState.Cpybck,
            DriveState.CBShld,
            DriveState.Rbld,
            DriveState.JBOD
        ]

        return self in good_states

    def is_configured(self) -> bool:
        """Check if drive is configured according to status"""
        configured_states = [
            DriveState.DHS,
            DriveState.GHS,
            # DriveState.Sntze, ??
            DriveState.Onln,
            DriveState.SED,
            # DriveState.UGShld, ??
            DriveState.HSPShld,
            DriveState.CFShld,
            DriveState.Cpybck,
            DriveState.CBShld,
            DriveState.Rbld,
            DriveState.JBOD
        ]

        return self in configured_states

    def is_settable(self) -> bool:
        """Check if this status can be directly set. Not all statuses can be set directly."""
        # online | offline | missing | good

        settable_states = [
            DriveState.Onln,
            DriveState.Offln,
            DriveState.Missing,
            DriveState.UGood,
            DriveState.JBOD
        ]

        return self in settable_states

    def settable_str(self) -> str:
        """Get string representation of settable status. Storcli uses different strings for set command than for show command."""
        if self == DriveState.Onln:
            return 'online'
        elif self == DriveState.Offln:
            return 'offline'
        elif self == DriveState.Missing:
            return 'missing'
        elif self == DriveState.UGood:
            return 'good'
        elif self == DriveState.JBOD:
            return 'jbod'
        else:
            raise ValueError('This status is not settable')

    @staticmethod
    def from_string(status: str) -> 'DriveState':
        """Get DriveState from string"""
        for drive_status in DriveState:
            if drive_status.name.lower() == status.lower() or drive_status.value.lower() == status.lower():
                return drive_status
        raise ValueError('Invalid drive status: {0}'.format(status))


class DriveMetrics(object):
    """StorCLI DriveMerics

    Instance of this class represents drive metrics

    Args:
        drive (:obj:Drive): drive object

    Properties:
        state (str): drive state
        shield_errors (str): number of shield errors on drive
        media_errors (str): number of media errors on drive
        predictive_failure (str): predictive failure on drive
        temperature (str): temperature of drive in celsius
        smart_alert (str): S.M.A.R.T alert flag on drive
        init_progress (str): % progress of initialization on a drive
        rebuild_progress (str): % progress of rebuild on a drive
        erase_progress (str): % progress of erase on a drive
        all (dict): all metrics
    """

    def __init__(self, drive):
        """Constructor - create StorCLI DriveMetrics object

        Args:
            cv (:obj:CacheVault): cachevault object
        """
        self._drive = drive

    @property
    def _show_all(self):
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._drive._run(args))

    @property
    def _resposne_state(self):
        key_prefix = 'Drive /c{0}/e{1}/s{2}'.format(
            self._drive.ctl_id,
            self._drive.encl_id,
            self._drive.id
        )
        detailed_info = self._show_all['{0} - Detailed Information'.format(
            key_prefix)]
        detailed_state = detailed_info['{0} State'.format(key_prefix)]
        return detailed_state

    @property
    def state(self) -> DriveState:
        """drive state

        Returns:
            DriveState: drive state
        """
        return self._drive.state

    @property
    @common.stringify
    def shield_errors(self):
        """(str): number of shield errors on drive
        """
        return self._resposne_state['Shield Counter']

    @property
    @common.stringify
    def media_errors(self):
        """(str): number of media errors on drive
        """
        return self._resposne_state['Media Error Count']

    @property
    @common.stringify
    def other_errors(self):
        """(str): number of other errors on drive
        """
        return self._resposne_state['Other Error Count']

    @property
    @common.stringify
    def predictive_failure(self):
        """predictive failure on drive
        """
        return self._resposne_state['Predictive Failure Count']

    @property
    def temperature(self):
        """temperature of drive in celsius
        """
        return self._resposne_state['Drive Temperature'].split('C')[0].lstrip()

    @property
    @common.upper
    def smart_alert(self):
        """(str): S.M.A.R.T alert flag on drive
        """
        return self._resposne_state['S.M.A.R.T alert flagged by drive']

    @property
    @common.stringify
    def init_progress(self):
        """Show initialization progress in percentage

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'initialization'
        ]

        progress = common.response_data(self._drive._run(args))[0]['Progress%']
        if progress == '-':
            return "100"
        return progress

    @property
    @common.stringify
    def rebuild_progress(self):
        """Show rebuild progress in percentage

        Returns:
            (str): rebuild in percentage
        """
        args = [
            'show',
            'rebuild'
        ]

        progress = common.response_data(self._drive._run(args))[0]['Progress%']
        if progress == '-':
            return "100"
        return progress

    @property
    @common.stringify
    def erase_progress(self):
        """Show drive erase progress in percentage

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'erase'
        ]

        progress = common.response_data(self._drive._run(args))[0]['Progress%']
        if progress == '-':
            return "100"
        return progress

    @property
    def all(self):
        """(:obj:DriveMetrics): all metrics
        """
        metrics = {}

        for attribute in dir(self):
            if not attribute.startswith('_') and not attribute == 'all':
                metrics[attribute] = self.__getattribute__(attribute)
        return metrics


class Drive(object):
    """StorCLI Drive

    Instance of this class represents drive in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        encl_id (str): enclosure id
        slot_id (str): slot id
        binary (str): storcli binary or full path to the binary

    Properties:
        id (str): drive id
        name (str): drive cmd name
        facts (dict): raw drive facts
        metrics (dict): drive metrics for monitoring
        size (str): drive size
        interface (str): SATA / SAS
        medium (str): SSD / HDD
        model (str): drive model informations
        serial (str): drive serial number
        wwn (str): drive wwn
        firmware (str): drive firmware version
        device_speed (str): drive speed
        linke_speed (str): drive connection link speed
        ctl_id (str): drive controller id
        ctl (:obj:controller.Controller): drive controller
        encl_id (str): drive enclosure
        encl (:obj:enclosure.Enclosure): drive enclosure
        phyerrorcounters (dict): drive error counters (also setter)
        state (str): drive state (also setter)
        spin (str): drive spin state (also setter)


    Methods:
        init_start (dict): starts the initialization process on a drive
        init_stop (dict): stops an initialization process running on a drive
        init_running (bool): check if initialization is running on a drive
        erase_start (dict): securely erases non-SED drive
        erase_stop (dict): stops an erase process running on a drive
        erase_running (bool): check if erase is running on a drive
        hotparedrive_create (dict): add drive to hotspares
        hotparedrive_delete (dict): delete drive from hotspare

    TODO:
        Implement missing methods:
            * start rebuild
            * stop rebuild
            * pause rebuild
            * resume rebuild
            * rebuild running
    """

    def __init__(self, ctl_id, encl_id, slot_id, binary='storcli64'):
        """Constructor - create StorCLI Drive object

        Args:
            ctl_id (str): controller id
            encl_id (str): enclosure id
            slot_id (str): slot id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._encl_id = encl_id
        self._slot_id = slot_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}/e{1}/s{2}'.format(self._ctl_id,
                                              self._encl_id, self._slot_id)

        self._exist()

    @staticmethod
    def _response_properties(out):
        return common.response_data(out)['Drive Information'][0]

    def _response_attributes(self, out):
        detailed_info = ('Drive /c{0}/e{1}/s{2}'
                         ' - Detailed Information'.format(self._ctl_id, self._encl_id, self._slot_id))
        attr = 'Drive /c{0}/e{1}/s{2} Device attributes'.format(
            self._ctl_id, self._encl_id, self._slot_id)
        return common.response_data(out)[detailed_info][attr]

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
        """(str): drive id
        """
        return self._slot_id

    @property
    def name(self):
        """(str): drive cmd name
        """
        return self._name

    @property
    def facts(self):
        """(dict): raw drive facts
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """(dict): drive metrics
        """
        return DriveMetrics(self)

    @property
    def size(self):
        """(str): drive size
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Size']

    @property
    @common.upper
    def interface(self):
        """(str): SATA / SAS
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Intf']

    @property
    @common.upper
    def medium(self):
        """(str): SSD / HDD
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Med']

    @property
    @common.upper
    @common.strip
    def model(self):
        """(str): drive model informations
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Model']

    @property
    @common.upper
    @common.strip
    def serial(self):
        """(str): drive serial number
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['SN']

    @property
    @common.upper
    def wwn(self):
        """(str): drive wwn
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['WWN']

    @property
    @common.upper
    def firmware(self):
        """(str): drive firmware version
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['Firmware Revision']

    @property
    def device_speed(self):
        """(str): drive speed
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['Device Speed']

    @property
    def link_speed(self):
        """(str): drive connection link speed
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['Link Speed']

    @property
    def ctl_id(self):
        """(str): drive controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): drive controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def encl_id(self):
        """(str): dirve enclosure id
        """
        return self._encl_id

    @property
    def encl(self):
        """(:obj:enclosure.Enclosure): drive enclosure
        """
        return enclosure.Enclosure(ctl_id=self._ctl_id, encl_id=self._encl_id, binary=self._binary)

    @property
    def vd_id(self) -> Union[None, int]:
        """(int): drive virtual drive id if any
        """
        args = [
            'show']
        dg = self._response_properties(self._run(args))['DG']

        if isinstance(dg, int):
            return dg
        else:
            return None

    @property
    def vd(self) -> Union[None, virtualdrive.VirtualDrive]:
        """(:obj:virtualdrive.VirtualDrive): get the virtual drive if any
        """
        if self.vd_id is None:
            return None
        else:
            return virtualdrive.VirtualDrive(self._ctl_id, self.vd_id, self._binary)

    def init_start(self):
        """Start initialization of a drive

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'start',
            'initialization'
        ]
        return common.response_cmd(self._run(args))

    def init_stop(self):
        """Stop initialization on a drive

        A stopped initialization process cannot be resumed.

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'stop',
            'initialization'
        ]
        return common.response_cmd(self._run(args))

    @property
    def init_running(self):
        """Check if initialization process is running on a drive

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'initialization'
        ]

        status = common.response_data(self._run(args))[0]['Status']
        return bool(status == 'In progress')

    def erase_start(self, mode='simple'):
        """Securely erases non-SED drives with specified erase pattern

        Args:
            mode (str):
                simple		-	Single pass, single pattern write
                normal		-	Three pass, three pattern write
                thorough	-	Nine pass, repeats the normal write 3 times
                standard	-	Applicable only for DFF's
                threepass	-	Three pass, pass1 random pattern write, pass2,3 write zero, verify
                crypto 	-	Applicable only for ISE capable drives
                PatternA|PatternB - an 8-Bit binary pattern to overwrite the data.

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'start',
            'erase',
            '{0}'.format(mode)
        ]
        return common.response_cmd(self._run(args))

    def erase_stop(self):
        """Stops the erase operation of a drive

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'stop',
            'erase'
        ]
        return common.response_cmd(self._run(args))

    @property
    def erase_running(self):
        """Check if erase process is running on a drive

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'erase'
        ]

        status = common.response_data(self._run(args))[0]['Status']
        return bool(status == 'In progress')

    @property
    def phyerrorcounters(self):
        """Get/Reset the drive phyerrorcounters

        Reset drive error counters with (str) 0
        """
        args = [
            'show',
            'phyerrorcounters'
        ]
        return common.response_data(self._run(args))[self._name]

    @phyerrorcounters.setter
    def phyerrorcounters_reset(self):
        """
        """
        args = [
            'reset',
            'phyerrorcounters'
        ]
        return common.response_cmd(self._run(args))

    @property
    def state(self) -> DriveState:
        """Get/Set drive state
        """
        args = [
            'show'
        ]

        state = self._response_properties(self._run(args))['State']

        return DriveState.from_string(state)

    @state.setter
    def state(self, value: Union[str, DriveState]):
        """ Set drive state
        """

        return self.set_state(value, force=False)

    def set_state(self, value: Union[str, DriveState], force: bool = False):
        """ Set drive state
        """
        # if DriveState, get the string value
        if isinstance(value, DriveState):
            value = value.settable_str()

        args = [
            'set',
            '{0}'.format(value)
        ]

        if force:
            args.append('force')

        return common.response_setter(self._run(args))

    @property
    def spin(self):
        """Get/Set drive spin status

        One of the following states can be set (str):
            up - spins up and set to unconfigured good
            down - spins down an unconfigured drive and prepares it for removal

        Returns:
            (str): up / down
        """
        args = [
            'show'
        ]

        spin = self._response_properties(self._run(args))['Sp']
        if spin == 'U':
            return 'up'
        return 'down'

    @spin.setter
    def spin(self, value):
        """
        """
        if value == 'up':
            spin = 'spinup'
        elif value == 'down':
            spin = 'spindown'
        else:
            spin = value

        args = [
            '{0}'.format(spin)
        ]
        return common.response_setter(self._run(args))

    def hotparedrive_create(self, dgs=None, enclaffinity=False, nonrevertible=False):
        """Creates a hotspare drive

        Args:
            dgs (str): specifies the drive group to which the hotspare drive is dedicated (N|0,1,2...)
            enclaffinity (bool): Specifies the enclosure to which the hotspare is associated with.
                                 If this option is specified, affinity is set; if it is not specified,
                                 there is no affinity.NOTE Affinity cannot be removed once it is set
                                 for a hotspare drive.
            nonrevertible (bool): sets the drive as a nonrevertible hotspare

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'add',
            'hotsparedrive'
        ]

        if dgs:
            args.append("dgs={0}".format(dgs))
        if enclaffinity:
            args.append('enclaffinity')
        if nonrevertible:
            args.append('nonrevertible')
        return common.response_cmd(self._run(args))

    def hotparedrive_delete(self):
        """Deletes drive from hotspares

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'delete',
            'hotsparedrive'
        ]
        return common.response_cmd(self._run(args))


class Drives(object):
    """StorCLI drives

    Instance of this class is iterable with :obj:Drive as item

    Args:
        ctl_id (str): controller id
        encl_id (str): enclosure id
        binary (str): storcli binary or full path to the binary

    Properties:
        ids (list of str): list of drives id
        ctl_id (str): controller id where drives are located
        encl_id (str): enclosure id where drives are located
        ctl (:obj:controller.Controller): controller
        encl (:obj:Enclosure): enclosure


    Methods:
        get_drive (:obj:Enclosure): return drive object by id
        get_drive_range_ids (list of int): return list of drive ids in range
        get_drive_range (:obj:Drives): return drives object in range
    """

    def __init__(self, ctl_id: int, encl_id: int, binary: str = 'storcli64'):
        """Constructor - create StorCLI Enclosures object

        Args:
            ctl_id (str): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id: int = ctl_id
        self._encl_id: int = encl_id
        self._binary: str = binary
        self._storcli: StorCLI = StorCLI(binary)

    @property
    def _drive_ids(self) -> List[int]:
        args = [
            '/c{0}/e{1}/sall'.format(self._ctl_id, self._encl_id),
            'show'
        ]

        if not self.encl.has_drives:
            return []

        drives = common.response_data(self._storcli.run(args))[
            'Drive Information']
        return [int(drive['EID:Slt'].split(':')[1]) for drive in drives]

    @property
    def _drives(self):
        for drive_id in self._drive_ids:
            yield Drive(ctl_id=self._ctl_id, encl_id=self._encl_id, slot_id=drive_id, binary=self._binary)

    def __iter__(self):
        return self._drives

    @property
    def ids(self) -> List[int]:
        """(list of str): list of enclosures id
        """
        return self._drive_ids

    @property
    def ctl_id(self) -> int:
        """(str): enclosures controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): enclosures controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def encl_id(self) -> int:
        """(str): enclosure id
        """
        return self._encl_id

    @property
    def encl(self):
        """(:obj:Enclosure): enclosure
        """
        return enclosure.Enclosure(ctl_id=self._ctl_id, encl_id=self._encl_id, binary=self._binary)

    def get_drive(self, drive_id: int) -> Optional[Drive]:
        """Get drive object by id

        Args:
            drive_id (str): drive id

        Returns:
            (None): no drive with id
            (:obj:Drive): drive object
        """
        if drive_id in self._drive_ids:
            return Drive(ctl_id=self._ctl_id, encl_id=self._encl_id, slot_id=drive_id, binary=self._binary)
        else:
            return None

    def __getitem__(self, drive_id: int) -> Optional[Drive]:
        return self.get_drive(drive_id)

    def get_drive_range_ids(self, drive_id_begin: Union[int, str], drive_id_end: Optional[int] = None) -> List[int]:
        """Get drive range list in the current enclosure

        Args:
            drive_id_begin (Union[int,str]): A range in format '1-10' or '1-10,20-30' or just an integer
            drive_id_end (Optional[int]): end of the range
        """

        if drive_id_end:
            # check that drive_id_begin is integer, if not raise exception
            if not isinstance(drive_id_begin, int):
                raise ValueError('drive_id_begin must be an integer')

            # otherwise convert to string
            drive_id_begin = '{0}-{1}'.format(drive_id_begin, drive_id_end)

        # if drive_id_begin is an integer, convert to string
        if isinstance(drive_id_begin, int):
            drive_id_begin = str(drive_id_begin)

        # get the list of drives
        drive_ids = []
        for drive_id in drive_id_begin.split(','):
            if '-' in drive_id:
                range_begin = drive_id.split('-')[0]
                range_end = drive_id.split('-')[1]
                drive_ids.extend(
                    range(int(range_begin), int(range_end) + 1))
            else:
                drive_ids.append(int(drive_id))

        return drive_ids

    def get_drive_range(self, drive_id_begin: Union[int, str], drive_id_end: Optional[int] = None):
        """Get drive range in the current enclosure

        Args:
            drive_id_begin (Union[int,str]): A range in format '1-10' or '1-10,20-30' or just an integer
            drive_id_end (Optional[int]): end of the range
        """
        drive_ids = self.get_drive_range_ids(drive_id_begin, drive_id_end)

        for drive_id in drive_ids:
            yield Drive(ctl_id=self._ctl_id, encl_id=self._encl_id, slot_id=drive_id, binary=self._binary)
