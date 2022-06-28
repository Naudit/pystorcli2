# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

class StorclifileSampleNotFound(Exception):
    def __init__(self, path, args=[]):
        args_str = ' '.join(args)
        super().__init__(
            f'Smartctlmockup didn\'t found requested file on {path}. This might be the simulating the call of "smartctl {args_str}"')
