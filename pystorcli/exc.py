# -*- coding: utf-8 -*-

# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# See LICENSE for details.

'''StorCLI exceptions
'''

import subprocess


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


class StorCliMissingError(StorCliError):
    """StorCLI missing object error
    """ 
    def __init__(self, obj_type, obj_name):
        super().__init__("Object '{0}' doesnt exist: {1}".format(obj_type, obj_name))


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
