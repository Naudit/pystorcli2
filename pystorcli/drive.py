# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI drive python module
'''

from . import StorCLI
from . import common
from . import controller
from . import enclosure


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
    def  _resposne_state(self):
        key_prefix = 'Drive /c{0}/e{1}/s{2}'.format(
            self._drive.ctl_id,
            self._drive.encl_id,
            self._drive.id
        )
        detailed_info = self._show_all['{0} - Detailed Information'.format(key_prefix)]
        detailed_state = detailed_info['{0} State'.format(key_prefix)]
        return detailed_state

    @property
    def state(self):
        """drive state
        Returns
            (str):
                dhs - dedicated hotspare to some virtual drive
                ghs - global hotspare
                bad - bad drive
                good - unconfigured good
                online - already in virtual drive with good state
                offline - already in virtual drive with bad state
        """
        return self._drive.state

    @property
    def shield_errors(self):
        """(str): number of shield errors on drive
        """
        return str(self._resposne_state['Shield Counter'])

    @property
    def media_errors(self):
        """(str): number of media errors on drive
        """
        return str(self._resposne_state['Media Error Count'])

    @property
    def other_errors(self):
        """(str): number of other errors on drive
        """
        return str(self._resposne_state['Other Error Count'])

    @property
    def predictive_failure(self):
        """predictive failure on drive
        """
        return str(self._resposne_state['Predictive Failure Count'])

    @property
    def temperature(self):
        """temperature of drive in celsius
        """
        return self._resposne_state['Drive Temperature'].split('C')[0].lstrip()

    @property
    @common.lower
    def smart_alert(self):
        """(str): S.M.A.R.T alert flag on drive
        """
        return self._resposne_state['S.M.A.R.T alert flagged by drive']

    @property
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
        self._name = '/c{0}/e{1}/s{2}'.format(self._ctl_id, self._encl_id, self._slot_id)

    @staticmethod
    def _response_properties(out):
        return common.response_data(out)['Drive Information'][0]

    def _response_attributes(self, out):
        detailed_info = ('Drive /c{0}/e{1}/s{2}'
                         ' - Detailed Information'.format(self._ctl_id, self._encl_id, self._slot_id))
        attr = 'Drive /c{0}/e{1}/s{2} Device attributes'.format(self._ctl_id, self._encl_id, self._slot_id)
        return common.response_data(out)[detailed_info][attr]

    def _run(self, args, **kwargs):
        args = args[:]
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

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
    @common.lower
    def interface(self):
        """(str): SATA / SAS
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Intf']

    @property
    @common.lower
    def medium(self):
        """(str): SSD / HDD
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Med']

    @property
    @common.lower
    def model(self):
        """(str): drive model informations
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Model']

    @property
    def serial(self):
        """(str): drive serial number
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['SN']

    @property
    @common.lower
    def wwn(self):
        """(str): drive wwn
        """
        args = [
            'show',
            'all'
        ]
        return self._response_attributes(self._run(args))['WWN']

    @property
    @common.lower
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
    def state(self):
        """Get/Set drive state

        One of the following states can be set (str):
            online - changes the drive state to online
            offline - changes the drive state to offline
            missing - marks a drive as missing
            good - changes the drive state to unconfigured good
            jbod - sets the drive state to JBOD

        Returns:
            (str):
                dhs - dedicated hotspare to some virtual drive
                ghs - global hotspare
                bad - bad drive
                good - unconfigured good
                online - already in virtual drive with good state
                offline - already in virtual drive with bad state
        """
        args = [
            'show'
        ]

        state = self._response_properties(self._run(args))['State']
        if state == 'DHS':
            return 'dhs'
        elif state == 'UBad':
            return 'bad'
        elif state == 'Onln':
            return 'online'
        elif state == 'Offln':
            return 'offline'
        elif state == 'GHS':
            return 'ghs'
        return 'good'

    @state.setter
    def state(self, value):
        """
        """
        # online | offline | missing | good
        args = [
            'set',
            '{0}'.format(value)
        ]
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
        return common.response_cmd(self._run(args))

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
