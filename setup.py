#!/usr/bin/env python
import os, sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_deps():
    f = open(os.path.join(ROOT_DIR, "requirements.pip"), 'r')
    return [l[:-1] for l in f.readlines()]

# README is required for distribution, but README.md is required for github,
#   so create README temporarily
is_distribution = 'sdist' in sys.argv or 'bdist_wininst' in sys.argv

if is_distribution:
    os.system('cp %s/README.md %s/README' % (ROOT_DIR, ROOT_DIR))

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

# cleanup README
if is_distribution:
    os.remove('%s/README' % ROOT_DIR)