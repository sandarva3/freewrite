#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="freewrite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        'console_scripts': [
            'freewrite=freewrite.main:main',
        ],
    },
    package_data={
        'freewrite': [
            'assets/*',
            'fonts/*',
            'app_icons/*',
        ],
    },
)
