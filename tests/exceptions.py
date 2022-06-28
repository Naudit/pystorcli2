# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

import re


class StorclifileSampleNotFound(Exception):
    def __init__(self, path, args=[]):
        args_str = ' '.join(args)
        args_str = re.sub('.json', '', args_str)
        super().__init__(
            f'pyStorCLImockup didn\'t found requested file on {path}. This might be the simulating the call of "storcli {args_str}"')
