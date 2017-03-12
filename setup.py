from setuptools import setup, find_packages

RELEASE_VERSION = '2.0.7'

setup(
    name='pybuildtool',
    version=RELEASE_VERSION,
    url='https://github.com/dozymoe/PyBuildTool',
    download_url='https://github.com/dozymoe/PyBuildTool/tarball/' +\
            RELEASE_VERSION,

    author='Fahri Reza',
    author_email='dozymoe@gmail.com',
    description='Build utility to manage web resources',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms='any',
    license='MIT',
    install_requires=[
        'pyyaml',
        'watchdog',
    ],
)

print('Copy the file: wscript from https://github.com/dozymoe/PyBuildTool.')
