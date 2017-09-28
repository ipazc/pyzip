#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, setuptools

__author__ = 'Iván de Paz Centeno'

def readme():
    with open('README.rst') as f:
        return f.read()

if sys.version_info < (3, 4, 1):
    sys.exit('Python < 3.4.1 is not supported!')

setup(name='pyzip',
      version='0.0.1',
      description='PyZip is a package for handling zip-in-memory content as a dictionary.',
      long_description=readme(),
      url='http://github.com/ipazc/pyzip',
      author='Iván de Paz Centeno',
      author_email='ipazc@unileon.es',
      license='MIT',
      packages=setuptools.find_packages(),
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      keywords="pyzip dict zip file zipfile memory in-memory",
      zip_safe=False)
