#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', encoding='utf8') as f:
    readme = f.read()

setup(
    name='golden_agents',
    version='0.0.1',

    description='Utility functions for thwe Golden Agents project',
    long_description=readme,
    long_description_content_type='text/markdown',

    author='Bram Buitendijk <bram.buitendijk@di.huc.knaw.nl>',
    author_email='bram.buitendijk@di.huc.knaw.nl',

    url='https://github.com/knaw-huc/ga-ner-experiment',
    license='MIT',

    packages=find_packages(exclude=('tests', 'docs')),
)
