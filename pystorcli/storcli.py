# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

'''StorCLI python class
'''

import os
import re
import json
import shutil
import threading
import subprocess

from . import common
from . import exc
from . import cmdRunner

_SINGLETON_STORCLI_MODULE_LOCK = threading.Lock()
_SINGLETON_STORCLI_MODULE_ENABLE = False


class StorCLI(object):
    """StorCLI command line wrapper

    Instance of this class is storcli command line wrapper

    Args:
        binary (str): storcli binary or full path to the binary

    Properties:
        cache_enable (boolean): enable disable resposne cache (also setter)
        cache (dict): get / set raw cache content

    Methods:
        run (dict): output data from command line
        check_response_status (): check ouput command line status from storcli
        clear_cache (): purge cache

    TODO:
        * implement TTL for cache

    """
    __singleton_instance = None
    __cache_lock = threading.Lock()
    __cache_enabled = False
    __response_cache = {}
    __cmdrunner = None

    def __new__(cls, *args, **kwargs):
        """Thread safe singleton
        """
        global _SINGLETON_STORCLI_MODULE_LOCK
        with _SINGLETON_STORCLI_MODULE_LOCK:
            if _SINGLETON_STORCLI_MODULE_ENABLE:
                if StorCLI.__singleton_instance is None:
                    StorCLI.__singleton_instance = super(
                        StorCLI, cls).__new__(cls)
                return StorCLI.__singleton_instance
            else:
                return super(StorCLI, cls).__new__(cls)

    def __init__(self, binary='storcli64', cmdrunner=None):
        """Constructor - create StorCLI object wrapper

        Args:
            binary (str): storcli binary or full path to the binary
        """

        if cmdrunner is None:
            if self.__cmdrunner is None:
                self.__cmdrunner = cmdRunner.CMDRunner()
        else:
            self.__cmdrunner = cmdrunner

        if _SINGLETON_STORCLI_MODULE_ENABLE:
            if not hasattr(self, '_storcli'):
                # do not override _storcli in singleton if already exist
                self._storcli = self.__cmdrunner.binaryCheck(binary)

        if not _SINGLETON_STORCLI_MODULE_ENABLE:
            # dont share singleton lock and binary
            self._storcli = self.__cmdrunner.binaryCheck(binary)
            self.__cache_lock = threading.Lock()

    @property
    def cache_enable(self):
        """Enable/Disable resposne cache (atomic)

        Returns:
            bool: true/false
        """

        return self.__cache_enabled

    @cache_enable.setter
    def cache_enable(self, value):
        with self.__cache_lock:
            self.__cache_enabled = value

    def clear_cache(self):
        """Clear cache (atomic)
        """
        with self.__cache_lock:
            self.__response_cache = {}

    @property
    def cache(self):
        """Get/Set raw cache

        Args:
            (dict): raw cache

        Returns:
            (dict): cache
        """
        return self.__response_cache

    @cache.setter
    def cache(self, value):
        with self.__cache_lock:
            self.__response_cache = value

    @staticmethod
    def check_response_status(cmd, out):
        """Check ouput command line status from storcli.

        Args:
            cmd (list of str): full command line
            out (dict): output from command line

        Raises:
            StorCliCmdError
        """
        cmd_status = common.response_cmd(out)
        if cmd_status['Status'] == 'Failure':
            if 'Detailed Status' in cmd_status:
                raise exc.StorCliCmdError(
                    cmd, "{0}".format(cmd_status['Detailed Status']))
            else:
                raise exc.StorCliCmdError(cmd, "{0}".format(cmd_status))

    def run(self, args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs):
        """Execute storcli command line with arguments.

        Run command line and check output for errors.

        Args:
            args (list of str): cmd line arguments (without binary)
            stdout (fd): controll subprocess stdout fd
            stderr (fd): controll subporcess stderr fd
            **kwargs: arguments to subprocess run

        Returns:
            dict: output data from command line

        Raises:
            exc.StorCliCmdError
            exc.StorCliRunTimeError
            exc.StorCliRunTimeout
        """
        cmd = [self._storcli]
        cmd.extend(args)
        # output in JSON format
        cmd.append('J')
        cmd_cache_key = ''.join(cmd)

        if self.cache_enable:
            if cmd_cache_key in self.__response_cache:
                return self.__response_cache[cmd_cache_key]

        with self.__cache_lock:
            try:
                ret = self.__cmdrunner.run(
                    args=cmd, stdout=stdout, stderr=stderr, universal_newlines=True, **kwargs)
                try:
                    ret_json = json.loads(ret.stdout)
                    self.check_response_status(cmd, ret_json)
                    ret.check_returncode()
                    if self.cache_enable:
                        self.__response_cache[cmd_cache_key] = ret_json
                    return ret_json
                except json.JSONDecodeError:
                    # :/
                    err = re.search('(^.*)Storage.*Command.*$',
                                    ret.stdout, re.MULTILINE | re.DOTALL).group(1)
                    raise exc.StorCliCmdError(cmd, err)
            except subprocess.TimeoutExpired as err:
                raise exc.StorCliRunTimeout(err)
            except subprocess.SubprocessError as err:
                raise exc.StorCliRunTimeError(err)

    # Singleton stuff
    @staticmethod
    def __set_singleton(value):
        global _SINGLETON_STORCLI_MODULE_ENABLE
        global _SINGLETON_STORCLI_MODULE_LOCK
        with _SINGLETON_STORCLI_MODULE_LOCK:
            _SINGLETON_STORCLI_MODULE_ENABLE = value

    @staticmethod
    def enable_singleton():
        """Enable StorCLI to be singleton on module level

        Use StorCLI singleton across all objects. All pystorcli 
        class instances use their own StorCLI object. With enabled cache
        we can speedup for example metric lookups.

        """
        StorCLI.__set_singleton(True)

    @staticmethod
    def disable_singleton():
        """Disable StoreCLI class as signleton
        """
        StorCLI.__set_singleton(False)

    @staticmethod
    def is_singleton() -> bool:
        """Check if singleton is enabled
        """
        return _SINGLETON_STORCLI_MODULE_ENABLE
