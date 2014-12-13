#!/usr/bin/env python

from setuptools  import setup

setup(
    name='PyBuildTool',
    version='1.0',
    description='Build utility to manage web resources',
    author='Fahri Reza',
    author_email='dozymoe@gmail.com',
    url='http://pybuildtool.fireh.biz.id',
    packages=['pybuildtool'],
    data_files=[('.', ['wscript'])],
    install_requires=['pyyaml', 'watchdog'],
)
