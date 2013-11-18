#!/usr/bin/env python
import os, sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# README is required for distribution, but README.md is required for github,
#   so create README temporarily
os.system('cp %s/README.md %s/README.txt' % (ROOT_DIR, ROOT_DIR))

sdict = dict(
    name = 'django-simple-social',
    packages = ['django_simple_social'],
    version='.'.join(map(str, __import__('django_simple_social').__version__)),
    description = 'A generic system for interacting with remote APIs '
                  'that need to create Django socials.',
    long_description=open('README.md').read(),
    url = 'https://github.com/mattsnider/Django-Simple-Social',
    author = 'Matt Snider',
    author_email = 'admin@mattsnider.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'admin@mattsnider.com',
    keywords = ['simple', 'social', 'linkedin', 'facebook', 'twitter'],
    license = 'MIT',
    install_requires=[
        # framework required for work with this library
        'django>=1.3',

        # social infrastructure library
        'django-social-user',

        # social network libraries
        'facebook-sdk',
        'linkedin-api-json-client',
        'twython',
    ],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)

# if setup tools are available, package using setup tools
# otherwise use default
try:
    from setuptools import setup
    setup(**sdict)
except ImportError:
    # install_requires is not a valid key for default distutils
    from distutils.core import setup
    sdict.pop("install_requires", None)
    setup(**sdict)

# cleanup README
os.remove('%s/README.txt' % ROOT_DIR)