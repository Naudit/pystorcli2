# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI python module
'''

import os
import re
import json
import shutil
import subprocess

from . import common
from . import exc


class StorCLI(object):
    """StorCLI command line wrapper
    """
    def __init__(self, binary='storcli64'):
        """Constructor - create StorCLI object wrapper

        Args:
            binary (str): storcli binary or full path to the binary
        """
        self.binary = binary
        self._storcli = self._binary(binary)

    @staticmethod
    def _binary(binary):
        """Verify and return full binary path
        """
        _bin = shutil.which(binary)
        if not _bin:
            raise exc.StorCliError("Cannot find storcli binary '%s' in path: %s" % (binary, os.environ['PATH']))
        return _bin

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
                raise exc.StorCliCmdError(cmd, "{0}".format(cmd_status['Detailed Status']))
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

        try:
            ret = subprocess.run(args=cmd, stdout=stdout, stderr=stderr, universal_newlines=True, **kwargs)
            try:
                ret_json = json.loads(ret.stdout)
                self.check_response_status(cmd, ret_json)
                ret.check_returncode()
                return ret_json
            except json.JSONDecodeError:
                # :/
                err = re.search('(^.*)Storage.*Command.*$', ret.stdout, re.MULTILINE | re.DOTALL).group(1)
                raise exc.StorCliCmdError(cmd, err)
        except subprocess.TimeoutExpired as err:
            raise exc.StorCliRunTimeout(err)
        except subprocess.SubprocessError as err:
            raise exc.StorCliRunTimeError(err)
