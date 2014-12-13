#!/usr/bin/env python

from setuptools  import setup
from setuptools.command.install import install as BaseInstall


def post_install_waf():
    from subprocess import call
    call('wafinstall')


class CustomInstall(BaseInstall):
    def run(self):
        BaseInstall.run(self)
        self.execute(post_install_waf, msg="Installing waf")


setup(
    name='PyBuildTool',
    version='1.0',
    description='Build utility to manage web resources',
    author='Fahri Reza',
    author_email='dozymoe@gmail.com',
    url='http://pybuildtool.fireh.biz.id',
    packages=['pybuildtool'],
    data_files=[('.', ['wscript'])],
    install_requires=['pyyaml', 'waftools', 'watchdog'],
    cmdclass={'install': CustomInstall},
)
