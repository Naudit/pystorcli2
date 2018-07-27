# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI virtual virtual drive python module
'''

from . import StorCLI
from . import common
from . import controller
from . import drive

class VirtualDrive(object):
    """StorCLI enclosure

    Instance of this class represents enclosure in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        vd_id (str): virtual drive id
        binary (str): storcli binary or full path to the binary

    Properties:
        id (str): virtual drive id
        facts (dict): virtual drive settings and other stuff
        metrics (dict): virtual drive metrics for monitoring
        raid (str): vitual drive raid level
        size (str): virtual drive size
        state (str): virtual drive state
        strip (str): virtual drive strip size
        os_exposed (bool): virtual drive exposed to the OS
        os_name (str): virtual drive device path (/dev/...)
        ctl_id (str): virtual drive controller
        ctl (:obj:controller.Controller): virtual drive controller
        drives (list of :obj:drive.Drive): virtual drive drives
        name (str): virtual drive name (also setter)
        bootdrive (str): virtual drive bootdrive (also setter)
        pdcache (str): current disk cache policy on a virtual drive (also setter)
        wrcache (str): write cache policy on a virtual drive (also setter)
        rdcache (str): read cache policy on a virtual drive (also setter)
        iopolicy (str): I/O policy on a virtual drive (also setter)
        autobgi (str): auto background initialization setting (also setter)

    Methods:
        init_start (dict): starts the initialization process on a virtual drive
        init_stop (dict): stops an initialization process running on a virtual drive
        init_running (bool): check if init is running
        init_progress (str): % progress of init
        erase_start (dict): securely erases non-SED drives
        erase_stop (dict): stops an erase process running on a virtual drive
        erase_running (bool): check if erase is running
        erase_progress (str): % progress of erase
        delete (dict): delete virtual drive
        migrate_start (dict): starts the migration process on a virtual drive
        migrate_stop (dict): stops an migration process running on a virtual drive
        migrate_running (bool): check if migrate is running
        migrate_progress (str):% progress of migrate
        get_vd (:obj:VirtualDrive): Get virtual drive object by id
        get_named_vd (:obj:VirtualDrive): Get virtual drive object by name

    Todo:
        * Facts
        * Metrics
    """
    def __init__(self, ctl_id, vd_id, binary='storcli64'):
        """Constructor - create StorCLI Drive object

        Args:
            ctl_id (str): controller id
            vd_id (str): virtual drive id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._vd_id = vd_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}/v{1}'.format(self._ctl_id, self._vd_id)

    def _run(self, args, **kwargs):
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

    @staticmethod
    def _response_properties(out):
        return common.response_data(out)['Virtual Drives'][0]

    def _response_properties_all(self, out):
        return common.response_data(out)['VD{0} Properties'.format(self._vd_id)]

    @staticmethod
    def _resposne_operation_status(out):
        return common.response_data(out)['VD Operation Status'][0]

    @property
    def id(self):
        """(str): virtual drive id
        """
        return self._vd_id

    @property
    def facts(self):
        """(dict): virtual drive settings and other stuff
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """(dict): virtual drive metrics for monitoring
        """
        pass

    @property
    @common.lower
    def raid(self):
        """(str): vitual drive raid level
        """
        args = [
            'show'
        ]

        return self._response_properties(self._run(args))['TYPE']

    @property
    def size(self):
        """(str): virtual drive size
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['Size']

    @property
    @common.lower
    def state(self):
        """(str): virtual drive state
        """
        args = [
            'show'
        ]
        return self._response_properties(self._run(args))['State']

    @property
    def strip(self):
        """(str): virtual drive strip size
        """
        args = [
            'show',
            'all'
        ]

        size = self._response_properties_all(self._run(args))['Strip Size']
        return size.split()[0]

    @property
    def os_exposed(self):
        """(bool): virtual drive exposed to the OS
        """
        args = [
            'show',
            'all'
        ]

        exposed = self._response_properties_all(self._run(args))['Exposed to OS']
        return bool(exposed == 'Yes')

    @property
    @common.lower
    def os_name(self):
        """(str): virtual drive device path (/dev/...)
        """
        args = [
            'show',
            'all'
        ]
        return self._response_properties_all(self._run(args))['OS Drive Name']

    @property
    def ctl_id(self):
        """(str): virtual drive controller
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): virtual drive controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def drives(self):
        """(list of :obj:Drive): virtual drive drives
        """
        args = [
            'show',
            'all'
        ]

        drives = []
        pds = common.response_data(self._run(args))['PDs for VD {0}'.format(self._vd_id)]
        for pd in pds:
            drive_encl_id, drive_slot_id = pd['EID:Slt'].split(':')
            drives.append(
                drive.Drive(
                    ctl_id=self._ctl_id,
                    encl_id=drive_encl_id,
                    slot_id=drive_slot_id,
                    binary=self._binary
                )
            )
        return drives

    @property
    def name(self):
        """Get/set virtual drive name

        Returns:
            (str): raid name
        """
        args = [
            'show',
        ]

        properties = self._response_properties(self._run(args))
        return properties['Name']

    @name.setter
    def name(self, value):
        """
        """
        args = [
            'set',
            'name={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    def bootdrive(self):
        """Get/set virtual drive as Boot Drive

        One of the following options can be set (str):
            on - enable boot virtual drive
            off - disable boot virtual dirve

        Returns:
            (str): on/off
        """
        args = [
            '/c{0}'.format(self._ctl_id),
            'show',
            'bootdrive'
        ]

        for vd in common.response_property(self._storcli.run(args)):
            if vd['Value'] == 'VD:{0}'.format(self._vd_id):
                return 'on'
        return 'off'

    @bootdrive.setter
    def bootdrive(self, value):
        """
        """
        args = [
            'set',
            'bootdrive={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    def pdcache(self):
        """Get/set PD Cache Setting

        One of the following options can be set (str):
            on - enables PD Caching
            off - disables PD Caching

        Returns:
            (str): on/off
        """
        args = [
            'show',
            'all'
        ]

        properties = self._response_properties_all(self._run(args))
        if properties['Disk Cache Policy'] == 'Enabled':
            return 'on'
        elif properties['Disk Cache Policy'] == 'Default':
            return 'default'
        return 'off'

    @pdcache.setter
    def pdcache(self, value):
        """
        """
        args = [
            'set',
            'pdcache={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    def wrcache(self):
        """Get/set Write cache setting

        One of the following options can be set (str):
            wt - write Through
            wb - write Back
            awb - write Back even in case of bad BBU also

        Returns:
            (str): wt/wb/awb
        """
        args = [
            'show',
        ]

        properties = self._response_properties(self._run(args))
        if 'AWB' in properties['Cache']:
            return 'awb'
        elif 'WB' in properties['Cache']:
            return 'wb'
        return 'wt'

    @wrcache.setter
    def wrcache(self, value):
        """
        """
        args = [
            'set',
            'wrcache={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    def rdcache(self):
        """Get/set Read cache setting

        One of the following options can be set (str):
            ra - Read Ahead
            nora - No Read Ahead

        Returns:
            (str): ra/nora
        """
        args = [
            'show',
        ]

        properties = self._response_properties(self._run(args))
        if properties['Cache'][0:2] == 'NR':
            return 'nora'
        return 'ra'

    @rdcache.setter
    def rdcache(self, value):
        """
        """
        args = [
            'set',
            'rdcache={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    def iopolicy(self):
        """Get/set iopolicy setting

        One of the following options can be set (str):
            cached - IOs are cached
            direct - IOs are not cached

        Returns:
            (str): cached/direct
        """
        args = [
            'show',
        ]

        properties = self._response_properties(self._run(args))
        if properties['Cache'][-1] == 'D':
            return 'direct'
        return 'cached'

    @iopolicy.setter
    @common.lower
    def iopolicy(self, value):
        """
        """
        args = [
            'set',
            'iopolicy={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    @property
    @common.lower
    def autobgi(self):
        """Get/set auto background initialization

        One of the following options can be set (str):
            on - enables autobgi
            off - disables autobgi

        Returns:
            (str): on/off
        """
        args = [
            'show',
            'autobgi'
        ]
        return self._resposne_operation_status(self._run(args))['AutoBGI']

    @autobgi.setter
    def autobgi(self, value):
        """
        """
        args = [
            'set',
            'autobgi={0}'.format(value)
        ]
        return common.response_setter(self._run(args))

    def init_start(self, full=False, force=False):
        """Starts the initialization of a virtual drive.

        Args:
            full (bool, optional): if specified then it is the full init otherwise it is Fast init
            force (bool, optional): must be set if there was before some user data

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'start',
            'init'
        ]

        if full:
            args.append('full')
        if force:
            args.append('force')
        return common.response_cmd(self._run(args))

    def init_stop(self):
        """Stops the initialization of a virtual drive.

        A stopped initialization process cannot be resumed.

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'stop',
            'init'
        ]
        return common.response_cmd(self._run(args))

    @property
    def init_running(self):
        """Check initialization process process.

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'init'
        ]

        status = self._resposne_operation_status(self._run(args))['Status']
        return bool(status == 'In progress')

    @property
    def init_progress(self):
        """Show virtual drive initialization Progress.

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'init'
        ]

        progress = self._resposne_operation_status(self._run(args))['Progress%']
        if progress == '-':
            return "100"
        return progress

    def erase_start(self, mode='simple'):
        """Securely erases non-SED drives with specified erasepattern.

        Args:
            mode (str, optional):
                simple		-	Single pass, single pattern write
                normal		-	Three pass, three pattern write
                thorough	-	Nine pass, repeats the normal write 3 times
                standard	-	Applicable only for DFF's
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
        """Stops the erase operation of a virtual drive.

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
        """Check erase process process.

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'erase'
        ]

        status = self._resposne_operation_status(self._run(args))['Status']
        return bool(status == 'In progress')

    @property
    def erase_progress(self):
        """Show virtual drive erase progress.

        Returns:
            (str): progress in percentage
        """

        args = [
            'show',
            'erase'
        ]

        progress = self._resposne_operation_status(self._run(args))['Progress%']
        if progress == '-':
            return "100"
        return progress

    def delete(self, force=False):
        """ Deletes a particular virtual drive.

        Args:
            force (bool, optional): If you delete a virtual drive with a valid MBR
                          without erasing the data and then create a new
                          virtual drive using the same set of physical drives
                          and the same RAID level as the deleted virtual drive,
                          the old unerased MBR still exists at block0 of the
                          new virtual drive, which makes it a virtual drive with
                          valid user data. Therefore, you must provide the
                          force option to delete this newly created virtual drive.

        Returns:
            (dict): resposne cmd data
        """
        args = [
            'del'
        ]

        if force:
            args.append('force')
        return  common.response_cmd(self._run(args))

    def migrate_start(self, option, drives, raid=None, force=False):
        """Starts migartion on the virtual drive.

        Args:
            option (str):
            	add - adds the specified drives to the migrated raid
            	remove - removes the specified drives from the migrated raid
            drives (str): specifies the list drives which needs to be added
                          or removed in storcli format ([e:]s|[e:]s-x|[e:]s-x,y])
            raid - raid level to which migration needs to be done (raid0, raid1, ...)
            force - if specified, then migration will start even if any drive in the DG is secured

        Returns:
           (dict): resposne cmd data
        """
        if not raid:
            raid = self.raid
        args = [
            'start',
            'migrate',
            'type={0}'.format(raid),
            'option={0}'.format(option),
            'drives={0}'.format(drives)
        ]
        if force:
            args.append('force')
        return  common.response_cmd(self._run(args))

    @property
    def migrate_running(self):
        """Check migrate process.

        Returns:
            (bool): true / false
        """
        args = [
            'show',
            'migrate'
        ]

        status = self._resposne_operation_status(self._run(args))['Status']
        return bool(status == 'In progress')

    @property
    def migrate_progress(self):
        """Show migrate progress.

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'migrate'
        ]

        progress = self._resposne_operation_status(self._run(args))['Progress%']
        if progress == '-':
            return "100"
        return progress


class VirtualDrives(object):
    """StorCLI virtual drives

    Instance of this class is iterable with indexing

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        ids (list of str): list of virtual drives id
        ctl_id (str): virtual drives controller id
        ctl (:obj:controller.Controller): virtual drives controller


    Methods:
        get_encl (:obj:VirtualDrive): return enclosure object by id
    """

    def __init__(self, ctl_id, binary='storcli64'):
        """Constructor - create StorCLI VirtualDrives object

        Args:
            ctl_id (str): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._binary = binary
        self._storecli = StorCLI(binary)

    @property
    def _vd_ids(self):
        args = [
            '/c{0}'.format(self._ctl_id),
            'show'
        ]
        data = common.response_data(self._storecli.run(args))
        if 'VD LIST' in data:
            return [vd['DG/VD'].split('/')[1] for vd in data['VD LIST']]
        return []

    @property
    def _vds(self):
        for vd_id in self._vd_ids:
            yield VirtualDrive(ctl_id=self._ctl_id, vd_id=vd_id, binary=self._binary)

    def __iter__(self):
        return self._vds

    @property
    def ids(self):
        """(list of str): list of virtual drives id
        """
        return self._vd_ids

    @property
    def ctl_id(self):
        """(str): virtual drives controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): virtual drives controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    def get_vd(self, vd_id):
        """Get virtual drive object by id

        Args:
            vd_id (str): virtual drive id

        Returns:
            None: no virtual drive with id
            :obj:`VirtualDrive`: virtual drive object
        """
        for vd in self:
            if vd.id == vd_id:
                return vd
        return None

    def get_named_vd(self, vd_name):
        """Get virtual drive object by name

        Args:
            vd_name (str): virtual drive name

        Returns:
            None: no virtual drive with name
            :obj:`VirtualDrive`: virtual drive object
        """
        for vd in self:
            if vd.name == vd_name:
                return vd
        return None
