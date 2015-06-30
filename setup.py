#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='PurpleBot',
    description='Mostly simple irc bot',
    author='Paul Traylor',
    url='http://github.com/kfdm/purplebot/',
    version='0.1',
    packages=find_packages(exclude=['test']),
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'purplebot = purplebot.cli.console:main',
            'purplebot-rpl = purplebot.cli.rpl:main',
            'purplebot-test = purplebot.test:main',
        ]
    }
)
