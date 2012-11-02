#!/usr/bin/env python
from os import path

ROOT_DIR = path.abspath(path.dirname(__file__))

def get_deps():
    f = open(path.join(ROOT_DIR, "requirements.pip"), 'r')
    return [l[:-1] for l in f.readlines()]

sdict = dict(
    name = 'django-simple-social',
    packages = ['django_simple_social'],
    version='.'.join(map(str, __import__('django_simple_social').__version__)),
    description = 'A generic system for interacting with remote APIs '
                  'that need to create Django socials.',
    long_description=open('README').read(),
    url = 'https://github.com/mattsnider/Django-Simple-Social',
    author = 'Matt Snider',
    author_email = 'admin@mattsnider.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'admin@mattsnider.com',
    keywords = ['simple', 'social', 'linkedin', 'facebook', 'twitter'],
    license = 'MIT',
    install_requires=get_deps(),
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

from distutils.core import setup
setup(**sdict)