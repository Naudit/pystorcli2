# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Martin Dojcak <martin@dojcak.sk>
# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
#
# This program is licensed under BSD 3-clause license.
# See LICENSE for details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
################################################################

from setuptools import setup
from subprocess import Popen, PIPE
import os
import re


def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()


def _get_version_match(content, path=''):
    # Search for lines of the form: # __version__ = 'ver'
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(regex, content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError(f"Unable to find version string in '{path}'.")


def get_version(path):
    try:
        p = Popen(['git', 'describe', '--always', '--tags'],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        describe = line.strip()[1:].decode('utf-8').split('-')
        if len(describe) == 1:
            return describe[0]
        else:
            return describe[0]+'.'+describe[1]

    except Exception as e:
        print(e)
        return _get_version_match(read_file(path), path)


def write_version(path):
    '''
    Write the version on variavle __version__ in version.py and returns the version
    '''
    version = get_version(os.path.join(path, 'version.py'))

    with open(os.path.join(path, 'version.py'), 'w') as f:
        f.write('__version__ = "{}"\n'.format(version))

    return version


def get_long_description():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    return long_description


REQUIREMENTS = [
]

CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Topic :: System :: Hardware :: Hardware Drivers',
    'Topic :: System :: Installation/Setup',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python',
]

setup(
    name="PyStorCLI2",
    version=write_version('pystorcli'),
    author="Rafael Leira",
    author_email="rafael.leira@naudit.es",
    description="StorCLI module wrapper 2",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Naudit/pystorcli2",
    packages=['pystorcli'],
    scripts=['bin/pystorcli-metrics'],
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': [
            # Requirements only needed for development
            'pytest',
            'pytest-cov',
            'coveralls',
        ]
    },
)
