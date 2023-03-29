#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup
from pathlib import Path
import sdist_upip

here = Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# load elements of version.py
exec(open(here / 'eeprom' / 'version.py').read())

setup(
    name='micropython-eeprom',
    version=__version__,
    description="MicroPython driver for AT24Cxx EEPROM",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brainelectronics/micropython-eeprom',
    author='brainelectronics',
    author_email='info@brainelectronics.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    keywords='micropython, i2c, eeprom, driver',
    project_urls={
        'Bug Reports': 'https://github.com/brainelectronics/micropython-eeprom/issues',
        'Source': 'https://github.com/brainelectronics/micropython-eeprom',
    },
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['eeprom'],
    install_requires=[]
)
