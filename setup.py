from setuptools import setup, find_packages
import os
import re


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as infile:
        text = infile.read()
    return text


def read_version(filename):
    return re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
            read(filename), re.MULTILINE).group(1)


setup(
    name='lidar-read',
    version=read_version('lidar/__init__.py'),
    author='Adam Dodge',
    author_email='Adam.Dodge@Colorado.edu',
    description='Set of tools for receiving data from LIDAR-Lite v3HP. ',
    long_description=read('README.rst'),
    scripts=['bin/lidar-read'],
    license='custom',
    url='https://github.com/ccarocean/lidar-read',
    packages=find_packages(),
    install_requires=[
        'pyjwt[crypto]',
        'requests',
        'smbus',
        'RPi.GPIO',
        'diskcache',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    zip_safe=False
)
