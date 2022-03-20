#!/usr/bin/env python3
from setuptools import setup, Extension

setup(name='c_ascii_converter', version='1.0', \
    ext_modules=[Extension('c_ascii_converter', ['src/c_extensions/ascii_converter.c'])]
)