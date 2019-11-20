#! /usr/bin/env python3

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
        name='django-postgres-setfield',
        version='0.0.1',
        package_dir={'setfield':'setfield'},
        packages=find_packages(),
        include_package_data=True,
        license='MIT License',
        description='Django field for storing sets, backed by Postgres arrays',
        long_description=README,
        url='https://github.com/CodeYellowBV/django-postgres-setfield',
        author='Peter Bex',
        author_email='peter@codeyellow.nl',
        test_suite='tests',
        classifiers=[
                'Environment :: Web Environment',
                'Framework :: Django',
                'Framework :: Django :: 2.1',
                'Framework :: Django :: 2.2',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.7',
                'Topic :: Database',
                'Topic :: Internet :: WWW/HTTP',
                'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
        install_requires=[
                'Django >= 2.1',
                # Disabled (for now?) due to https://github.com/CodeYellowBV/django-relativedelta/issues/6
                # We never import it directly from the code, so that is okay
                #'psycopg2 >= 2.8.4',
        ],
        tests_require=[
                # The tests do need psycopg2
                'psycopg2 >= 2.8.4',
        ],
)
