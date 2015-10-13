# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='polyrents-challenge',
    version='0.0.1',
    author='Nick Frost',
    author_email='nickfrostatx@gmail.com',
    description='Application security challenge',
    include_package_data=True,
    install_requires=[
        'bcrypt',
        'Flask',
        'redis',
    ],
)
