""" Setup module for AudioController """

import audiocontrol

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='audiocontrol',
    version=audiocontrol.__version__,
    description='A program that manages different audio players',
    #   long_description=long_description,
    url='https://github.com/hifiberry/audiocontrol',
    author='HiFiBerry',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Environment :: No Input/Output (Daemon),'
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX'
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3',

    install_requires=[
        'pyalsaaudio',
        'keyboard',
        'nuimo',
        'spotipy',
        'zeroconf',
        'bottle',
        'xmltodict',
        'lmnotify'
    ],

    keywords='audio control shairport spotifyd metadata',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    package_data={
        'config-example': ['configuration-example.txt'],
    },

    project_urls={
        'Bug Reports': 'https://github.com/hifiberry/audiocontrol/issues',
    },
    scripts=['bin/audiocontrol', 
             'bin/print-keycodes'],
)
