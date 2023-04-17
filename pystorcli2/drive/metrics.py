# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI drive metrics
'''

from .. import common

from typing import Union, List, Optional

from .state import DriveState


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
