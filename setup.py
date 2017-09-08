# coding=utf-8
import sys

from setuptools import find_packages
from setuptools import setup

assert sys.version_info[0] == 3 and sys.version_info[1] >= 5, "conductor requires Python 3.5 or newer"

setup(
    name='conductor',
    version='0.3.0',
    description='Steem Witness Toolkit',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'pytest-pylint',
                   'pytest-console-scripts'],
    install_requires=[
        'Click',
        'click-spinner',
        'tabulate',
        'requests',
        'prettytable',
    ],
    dependency_links=[
       'git+git://github.com/Netherdrake/steem-python'
    ],
    entry_points={
        'console_scripts': [
            'conductor=conductor.cli:conductor',
        ]
    })
