# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI foreign configuration python module
'''

from .. import StorCLI
from .. import common
from .. import controller
from .. import exc


class ForeignConfigurations(object):
    """StorCLI foreign configurations

    Instance of this class represents foreign configurations in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        facts (dict): raw foreign configuration facts
        ctl_id (str): foreign configuration controller
        ctl (:obj:controller.Controller): foreign configuration controller
        drives (list of :obj:drive.Drive): foreign configuration drives

    Methods:
        import (dict): imports the foreign configurations of a controller
        delete (dict): deletes the foreign configuration of a controller

    """

    def __init__(self, ctl_id: int, binary: str = 'storcli64'):
        """Constructor - create StorCLI Foreign Configuration object

        Args:
            ctl_id (str): controller id
            fc_id (str): foreign configuration id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id: int = ctl_id
        self._binary: str = binary
        self._storcli: StorCLI = StorCLI(binary)
        self._name: str = '/c{0}/fall'.format(self._ctl_id)

        self._exist()

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
    def ctl_id(self):
        """(str): foreign configuration controller id
        """
        return self._ctl_id

    @property
    def ctl(self):
        """(:obj:controller.Controller): foreign configuration controller
        """
        return controller.Controller(ctl_id=self._ctl_id, binary=self._binary)

    @property
    def facts(self):
        """(dict): raw foreign configuration facts
        """
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def has_foreign_configurations(self) -> bool:
        """(bool): true if controller has foreign configurations
        """
        args = [
            'show'
        ]

        try:
            fcs = common.response_data(self._run(args))['Total foreign Drive Groups']
            if fcs > 0:
                return True
        except KeyError:
            pass
        return False

    def delete_foreign_configurations(self, securitykey: str = None):
        """Deletes a foreign configuration

        Returns:
            (dict): response cmd data
        """
        args = [
            'del'
        ]

        if securitykey:
            args.append(f'securitykey={securitykey}')
        return common.response_cmd(self._run(args))

    def import_foreign_configurations(self, securitykey: str = None):
        """Imports a foreign configuration

        Returns:
            (dict): response cmd data
        """
        args = [
            'del'
        ]
        if securitykey:
            args.append(f'securitykey={securitykey}')
        return common.response_cmd(self._run(args))
