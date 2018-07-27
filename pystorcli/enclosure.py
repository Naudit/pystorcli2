# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI enclosure python module
'''

from . import StorCLI
from . import common
from . import controller
from . import drive


class Enclosure(object):
    """StorCLI enclosure

    Instance of this class represents enclosure in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        encl_id (str): enclosure id
        binary (str): storcli binary or full path to the binary

    Properties:
        id (str): enclosure id
        name (str): enclosure cmd name
        facts (dict): enclosure settings and other stuff
        metrics (dict): enclosure metrics for monitoring
        ctl_id (str): enclosure controller
        ctl (:obj:controller.Controller): enclosure controller
        drives (list of :obj:drive.Drive): enclosure drives

    Todo:
        * Facts
        * Metrics
    """
    def __init__(self, ctl_id, encl_id, binary='storcli64'):
        """Constructor - create StorCLI Enclosure object

        Args:
            ctl_id (str): controller id
            encl_id (str): enclosure id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._encl_id = encl_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}/e{1}'.format(self._ctl_id, self._encl_id)

    def _run(self, args, **kwargs):
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

    @property
    def id(self):
        """(str): enclosure id
        """
        return self._encl_id

    @property
    def name(self):
        """(str): enclosure cmd name
        """
        return self._name

    @property
    def facts(self):
        """(dict): enclosure settings and other stuff
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """(dict): enclosure metrics for monitoring
        """
        pass

    @property
    def ctl_id(self):
        """(str): enclosure controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): enclosure controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def _slot_ids(self):
        args = [
            'show',
            'status'
        ]

        status = common.response_data(self._run(args))['Enclosure /c{0}/e{1} '.format(self._ctl_id, self._encl_id)]
        return [drive['Slot'] for drive in status['Slot Info'] if drive['Status'] == "OK"]

    @property
    def drives(self):
        """(list of :obj:drive.Drive): enclosure drives
        """
        drives = []
        for slot_id in self._slot_ids:
            drives.append(
                drive.Drive(
                    ctl_id=self._ctl_id,
                    encl_id=self._encl_id,
                    slot_id=slot_id,
                    binary=self._binary
                )
            )
        return drives


class Enclosures(object):
    """StorCLI enclosures

    Instance of this class is iterable

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        ids (list of str): list of enclosures id
        ctl_id (str): enclosures controller id
        ctl (:obj:controller.Controller): enclosures controller


    Methods:
        get_encl (:obj:Enclosure): return enclosure object by id
    """

    def __init__(self, ctl_id, binary='storcli64'):
        """Constructor - create StorCLI Enclosures object

        Args:
            ctl_id (str): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._binary = binary
        self._storecli = StorCLI(binary)

    @property
    def _encl_ids(self):
        args = [
            '/c{0}/eall'.format(self._ctl_id),
            'show'
        ]
        out = self._storecli.run(args)
        return [encl['EID'] for encl in common.response_data(out)['Properties']]

    @property
    def _encls(self):
        for encl_id in self._encl_ids:
            yield Enclosure(ctl_id=self._ctl_id, encl_id=encl_id, binary=self._binary)

    def __iter__(self):
        return self._encls

    @property
    def ids(self):
        """(list of str): list of enclosures id
        """
        return self._encl_ids

    @property
    def ctl_id(self):
        """(str): enclosures controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): enclosures controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    def get_encl(self, encl_id):
        """Get enclosure object by id

        Args:
            encl_id (str): enclosure id

        Returns:
            None: no enclosure with id
            :obj:`Enclosure`: enclosure object
        """
        for encl in self:
            if encl.id == encl_id:
                return encl
        return None
