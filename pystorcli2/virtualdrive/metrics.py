# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI virtual virtual drive python module
'''

from . import common


class VirtualDriveMetrics(object):
    """StorCLI VirtualDriveMerics

    Instance of this class represents drive metrics

    Args:
        vd (:obj:VirtualDrive): virtual drive object

    Properties:
        state (str): virtual drive state
        init_progress (str): % progress of initialization on a virtual drive
        cc_progress (str): % progress of consistency check on a virtual drive
        migrate_progress (str): % progress of migration on a virtual drive
        erase_progress (str): % progress of erase on a virtual drive
        all (dict): all metrics
    """

    def __init__(self, vd):
        """Constructor - create StorCLI VirtualDriveMetrics object

        Args:
            vd (:obj:VirtualDrive): vitual drive object
        """
        self._vd = vd

    @property
    def state(self):
        """(str): virtual drive state (optimal | recovery | offline | degraded | degraded_partially)
        """
        return self._vd.state

    @property
    @common.stringify
    def init_progress(self):
        """Show virtual drive initialization progress in perctentage

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'init'
        ]

        progress = self._vd._resposne_operation_status(self._vd._run(args))[
            'Progress%']
        if progress == '-':
            return "100"
        return progress

    @property
    @common.stringify
    def cc_progress(self):
        """Show virtual drive consistency check progress in perctentage

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'cc'
        ]

        progress = self._vd._resposne_operation_status(self._vd._run(args))[
            'Progress%']
        if progress == '-':
            return "100"
        return progress

    @property
    @common.stringify
    def migrate_progress(self):
        """Show migrate progress of a virtual drive in percentage

        Returns:
            (str): progress in percentage
        """
        args = [
            'show',
            'migrate'
        ]

        progress = self._vd._resposne_operation_status(self._vd._run(args))[
            'Progress%']
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
