# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI controller python module
'''

from . import StorCLI
from . import common
from . import enclosure
from . import virtualdrive


class Controller(object):
    """StorCLI Controller

    Instance of this class represents controller in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        id (str): controller id
        name (str): controller cmd name
        facts (dict): controller settings and other stuff
        metrics (dict): controller metrics for monitoring
        vds (list of :obj:virtualdrive.VirtualDrives): controller virtual drives
        encls (:obj:enclosure.Enclosures): controller enclosures

    Methods:
        create_vd (:obj:VirtualDrive): create virtual drive (raid)

    Todo:
        * Facts
        * Metrics

    """
    def __init__(self, ctl_id, binary='storcli64'):
        """Constructor - create StorCLI Controller object

        Args:
            ctl_id (srt): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}'.format(self._ctl_id)

    def __str__(self):
        return '{0}'.format(common.response_data(self._run(['show'])))

    def _run(self, args, **kwargs):
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

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
        """ (dict): controller settings and other stuff
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """ metrics (dict): controller metrics for monitoring
        """
        pass

    @property
    def vds(self):
        """(:obj:virtualdrive.VirtualDrives): controller virtual drives
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
            name (str): raid name
            raid (str): raid level (raid0, raid1, ...)
            drives (str): storcli drives expression (e:s|e:s-x|e:s-x,y;e:s-x,y,z)
            strip (str, optional): raid strip size

        Returns:

        Raises:
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

    Instance of this class is iterable

    Args:
        binary (str): storcli binary or full path to the binary

    Properties:
        ids (list of str): list of controllers id

    Methods:
        get_clt (Controller): return controller object by id
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
            None: no controller with id
            :obj:`Controller`: controller object
        """
        for ctl in self:
            if ctl.id == ctl_id:
                return ctl
        return None
