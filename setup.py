from setuptools import setup

version = '1.3.0'
classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: X11 Applications :: KDE
License :: OSI Approved :: BSD License
Operating System :: POSIX
Operating System :: Unix
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Topic :: Desktop Environment :: K Desktop Environment (KDE)
Topic :: Software Development
Topic :: Software Development :: Quality Assurance
Topic :: System :: System Shells
Topic :: Utilities
"""

setup(
    name='pyprof2calltree',
    version=version,
    description="Help visualize profiling data from cProfile with kcachegrind and qcachegrind",
    long_description=open('README.txt').read(),
    keywords='profiler visualization programming tool kde kcachegrind qcachegrind',
    classifiers=[c for c in classifiers.split("\n") if c and c.strip()],
    author='Olivier Grisel',
    author_email='olivier.grisel@ensta.org',
    maintainer='Peter Waller',
    maintainer_email='p@pwaller.net',
    url='http://github.com/pwaller/pyprof2calltree/',
    license='BSD',
    py_modules = ['pyprof2calltree'],
    zip_safe=True,
    entry_points = {
        'setuptools.installation': [
            'eggsecutable = pyprof2calltree:main',
        ],
        'console_scripts': [
            'pyprof2calltree = pyprof2calltree:main',
        ],
    }
)
