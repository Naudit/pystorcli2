# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI cachevault python module
'''

from . import StorCLI
from . import common


class CacheVaultMetrics(object):
    """StorCLI CacheVaultMerics

    Instance of this class represents cache vault metrics

    Args:
        cv (:obj:CacheVault): cache vault object

    Properties:
        temperature (str): cache vault temperature in celsius
        state (str): cache vault state
        replacement_required (str): check if cache vault replacement is required
        offload_status (str): check if cache vault has got space to cache offload
        all (dict): all metrics
    """
    def __init__(self, cv):
        """Constructor - create StorCLI CacheVaultMetrics object

        Args:
            cv (:obj:CacheVault): cachevault object
        """
        self._cv = cv

    @property
    def _show_all(self):
        args = [
            'show',
            'all'
        ]
        return common.response_data(self._cv._run(args))

    def _response_property(self, data):
        return [(i['Property'], i['Value']) for i in data]

    @property
    def _info(self):
        return self._show_all['Cachevault_Info']

    @property
    def _firmware_satus(self):
        return self._show_all['Firmware_Status']

    @property
    def temperature(self):
        """(str): cache vault temperature in celsius
        """
        for key, value in self._response_property(self._info):
            if key == 'Temperature':
                return value.split()[0]
        return None

    @property
    @common.lower
    def state(self):
        """(str): cache vault state (optimal | ??? | unknown )
        FIXME: need to know all possible states of the cache vault (string from binary doesnt help)
        """
        for key, value in self._response_property(self._info):
            if key == 'State':
                return value
        return 'unknown'

    @property
    @common.lower
    def replacement_required(self):
        """(str): check if cache vault replacement is required
        """
        for key, value in self._response_property(self._firmware_satus):
            if key == 'Replacement required':
                return value
        return 'unknown'

    @property
    def offload_status(self):
        """(str): cache offload space ( ok | fail | unknown)
        """
        for key, value in self._response_property(self._firmware_satus):
            if key == 'No space to cache offload':
                if value == 'No':
                    return 'ok'
                else:
                    return 'fail'
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


class CacheVault(object):
    """StorCLI CacheVault

    Instance of this class represents cachevault in StorCLI hierarchy

    Args:
        ctl_id (str): controller id
        binary (str): storcli binary or full path to the binary

    Properties:
        facts (dict): raw cache vault facts
        metrics (:obj:CacheVaultMetrics): cache vault metrics

    Methods:
        create_vd (:obj:VirtualDrive): create virtual drive

    """
    def __init__(self, ctl_id, binary='storcli64'):
        """Constructor - create StorCLI CacheVault object

        Args:
            ctl_id (str): controller id
            binary (str): storcli binary or full path to the binary
        """
        self._ctl_id = ctl_id
        self._binary = binary
        self._storcli = StorCLI(binary)
        self._name = '/c{0}/cv'.format(self._ctl_id)

    def _run(self, args, **kwargs):
        args = args[:]
        args.insert(0, self._name)
        return self._storcli.run(args, **kwargs)

    @property
    def facts(self):
        args=[
            'show',
            'all'
        ]
        return common.response_data(self._run(args))

    @property
    def metrics(self):
        """(:obj:CacheVaultMetrics): cache vault metrics
        """
        return CacheVaultMetrics(self)
