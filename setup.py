#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
import glob
import os

home = os.path.expanduser("~")
setup(
name='cloudmesh_auth',
version = '0.1',
description='A secure rest framework for Cloudmesh',
packages=['cloudmesh_auth']
)

