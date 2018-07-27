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


class StorCLI(object):
    """StorCLI command line wrapper
    """
    def __init__(self, binary='storcli64'):
        """Constructor - create StorCLI object wrapper for cmd line

        Args:
            binary (str): storcli binary or full path to the binary
        """
        self.binary = binary
        self._storcli = self._binary(binary)

    @staticmethod
    def _binary(binary):
        """Verify and return full binary path
        """
        binary = shutil.which(binary)
        if not binary:
            raise StorCliError("Cannot find storcli binary '%s' in path: %s" % (binary, os.environ['PATH']))
        return binary

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
                raise StorCliCmdError(cmd, "{0}".format(cmd_status['Detailed Status']))
            else:
                raise StorCliCmdError(cmd, "{0}".format(cmd_status))

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
            StorCliCmdError
            StorCliRunTimeError
            StorCliRunTimeout
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
                raise StorCliCmdError(cmd, err)
        except subprocess.TimeoutExpired as err:
            raise StorCliRunTimeout(err)
        except subprocess.SubprocessError as err:
            raise StorCliRunTimeError(err)


class StorCliError(Exception):
    """StorCLI general exception
    """
    pass


class StorCliCmdError(StorCliError):
    """StorCLI command output error
    """
    def __init__(self, cmd, msg):
        msg = msg.lstrip().rstrip()
        super().__init__("Command '{0}' error: {1}".format(' '.join(cmd), msg))


class StorCliRunError(StorCliError):
    """StorCLI general subprocess exception
    """
    def __init__(self, ctx, *args, **kwargs):
        super().__init__(ctx, *args, **kwargs)
        self.cmd = ctx.cmd if isinstance(ctx, subprocess.SubprocessError) else ctx.args
        self.stderr = ctx.stderr
        self.stdout = ctx.stdout


class StorCliRunTimeError(StorCliRunError):
    """StorCLI subprocess ret code exception
    """
    def __init__(self, ctx, *args, **kwargs):
        super().__init__(ctx, *args, **kwargs)
        self.retcode = ctx.returncode if isinstance(ctx, subprocess.CalledProcessError) else None

    def __str__(self):
        return ("Command '{0}' returned with non-zero exit status "
                "{1}: {2}".format(' '.join(self.cmd), self.retcode, self.stderr))


class StorCliRunTimeout(StorCliError):
    """StorCLI subprocess timeout exception
    """
    def __init__(self, ctx, *args, **kwargs):
        super().__init__(ctx, *args, **kwargs)
        self.timeout = ctx.timeout

    def __str__(self):
        return ("Command '{0}' timeout after "
                "{1}: {2}, {3}".format(' '.join(self.cmd), self.timeout, self.stdout, self.stderr))
