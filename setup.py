from setuptools import setup, find_packages

setup(
    name='PurpleBot',
    description='Mostly simple discord bot',
    author='Paul Traylor',
    url='http://github.com/kfdm/purplebot/',
    version='0.1',
    packages=find_packages(exclude=['test']),
    install_requires=[
        'discord.py',
        'requests',
    ],
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
            'purplebot-discord = purplebot.discord:main',
        ]
    }
)
