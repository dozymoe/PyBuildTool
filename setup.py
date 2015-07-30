#!/usr/bin/env python

from setuptools  import setup

setup(
    name='PyBuildTool',
    version='1.1.1',
    description='Build utility to manage web resources',
    author='Fahri Reza',
    author_email='dozymoe@gmail.com',
    url='https://github.com/dozymoe/PyBuildTool',
    packages=['pybuildtool'],
    data_files=[('.', ['wscript'])],
    install_requires=['pyyaml', 'watchdog'],
)
