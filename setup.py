import os
import setuptools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="pystorcli",
    version="0.2.1",
    author="Martin Dojcak",
    author_email="martin@dojcak.sk",
    description="StorCLI module wrapper",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/Chillisystems/pystorcli",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
    ),
)