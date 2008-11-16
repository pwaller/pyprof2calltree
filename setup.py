from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(
    name='pyprof2calltree',
    version=version,
    description="Convert profiling data from cProfile to kcachegrind input format",
    long_description=file('README.txt').read(),
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='profiling visualization programming tool kde',
    author='Olivier Grisel',
    author_email='olivier.grisel@ensta.org',
    url='http://www.bitbucket.org/ogrisel/pyprof2calltree/src/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points = {
        'setuptools.installation': [
            'eggsecutable = pyprof2calltree:main',
        ],
        'console_scripts':
            ['pyprof2calltree = pyprof2calltree:main'],

    }
)
