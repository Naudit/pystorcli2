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
import pystorcli2
from typing import Optional, Dict, Any, List

from . import common
from . import exc
from . import cmdRunner
from .errors import StorcliError

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
    __response_cache: Dict[str, Any] = {}
    __cmdrunner = cmdRunner.CMDRunner()

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

    def __init__(self, binary='storcli64', cmdrunner: Optional[cmdRunner.CMDRunner] = None):
        """Constructor - create StorCLI object wrapper

        Args:
            binary (str): storcli binary or full path to the binary
        """

        if cmdrunner is not None:
            self._storcli = cmdrunner.binaryCheck(binary)
        else:
            self._storcli = self.__cmdrunner.binaryCheck(binary)

        if cmdrunner is not None:
            self.__cmdrunner = cmdrunner

        if not _SINGLETON_STORCLI_MODULE_ENABLE:
            self.__cache_lock = threading.Lock()

    def set_cmdrunner(self, cmdrunner: cmdRunner.CMDRunner):
        """
        Set command runner object.
        This is only useful for testing.
        """
        self.__cmdrunner = cmdrunner

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
    def check_response_status(cmd: List[str], out: Dict[str, Dict[int, Dict[str, Any]]], allow_error_codes: List[StorcliError]) -> bool:
        """Check ouput command line status from storcli.

        Args:
            cmd (list of str): full command line
            out (dict): output from command line
            raise_on_error (bool): raise exception on error (default: True)

        Returns:
            bool: True if no error found in output. False if error found but allowed. Raise exception otherwise.

        Raises:
            StorCliCmdError: if error found in output and not allowed
            StorCliCmdErrorCode: if error code found in output and not allowed
        """
        retcode = True
        cmd_status = common.response_cmd(out)
        if cmd_status['Status'] == 'Failure':
            if 'Detailed Status' in cmd_status:
                allowed_errors = True
                # Check if the error code is allowed
                for error in cmd_status['Detailed Status']:

                    if 'ErrCd' in error:
                        if StorcliError.get(error['ErrCd']) not in allow_error_codes:
                            allowed_errors = False
                    else:
                        allowed_errors = False

                    retcode = False
                    if not allowed_errors:
                        raise exc.StorCliCmdErrorCode(
                            cmd, StorcliError.get(error['ErrCd']))

                # Otherwise, raise an exception
                if not allowed_errors:
                    raise exc.StorCliCmdError(
                        cmd, "{0}".format(cmd_status['Detailed Status']))
            else:
                # Try to get the error code using description
                if 'Description' in cmd_status:
                    error_code = StorcliError.get(cmd_status['Description'])

                    if error_code != StorcliError.INVALID_STATUS:
                        if error_code not in allow_error_codes:
                            raise exc.StorCliCmdErrorCode(cmd, error_code)
                        else:
                            return False

                raise exc.StorCliCmdError(cmd, "{0}".format(cmd_status))

        return retcode

    def run(self, args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, allow_error_codes: List[StorcliError] = [], **kwargs):
        """Execute storcli command line with arguments.

        Run command line and check output for errors.

        Args:
            args (list of str): cmd line arguments (without binary)
            stdout (fd): controll subprocess stdout fd
            stderr (fd): controll subporcess stderr fd
            allow_error_codes (list of StorcliErrors): list of error codes to allow
            **kwargs: arguments to subprocess run

        Returns:
            dict: output data from command line

        Raises:
            exc.StorCliCmdError
            exc.StorCliCmdErrorCode
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
                    args=cmd, universal_newlines=True, **kwargs)
                try:
                    ret_json = json.loads(ret.stdout)
                    self.check_response_status(
                        cmd, ret_json, allow_error_codes)
                    if ret.returncode != 0:
                        raise subprocess.CalledProcessError(
                            ret.returncode, cmd, ret.stdout, ret.stderr)
                    if self.cache_enable:
                        self.__response_cache[cmd_cache_key] = ret_json
                    return ret_json
                except json.JSONDecodeError as err:
                    # legacy handler (Ralequi: I don't know if this is still needed or what exactly it does)
                    output = re.search('(^.*)Storage.*Command.*$',
                                       ret.stdout, re.MULTILINE | re.DOTALL)
                    if output:
                        raise exc.StorCliCmdError(cmd, output.group(1))

                    # Check if we can still parse the output
                    parsed = {}
                    for line in ret.stdout.splitlines():
                        if '=' in line:
                            key, value = line.split('=', 1)
                            parsed[key.strip()] = value.strip()

                    if 'Status' in parsed:
                        return parsed
                    else:
                        raise exc.StorCliCmdError(cmd, str(err))

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

    @property
    def full_version(self) -> str:
        """Get storcli version as storcli returns
        """
        out = self.run(['show'])
        version = common.response_cmd(out)['CLI Version']

        return version

    @property
    def version(self) -> str:
        """Get storcli version in a cleaner way
        """
        import re

        # Remove duplicated 0s
        first_clean = re.sub('0+', '0', self.full_version.split(' ')[0])

        # Remove leading 0s
        second_clean = re.sub('^0+', '', first_clean)

        return second_clean

    @property
    def controllers(self) -> 'pystorcli2.controller.Controllers':
        """Get list of controllers
        """
        from . import Controllers

        return Controllers(binary=self._storcli)
