Overview
========

Script to help visualize profiling data collected with the cProfile
python module with the kcachegrind_ (screenshots_) graphical calltree
analyser.

This is a rebranding of the venerable
http://www.gnome.org/~johan/lsprofcalltree.py script by David Allouche
et Al. It aims at making it easier to distribute (e.g. through pypi)
and behave more like the scripts of the debian kcachegrind-converters_
package. The final goal is to make it part of the official upstream
kdesdk_ package.

.. _kcachegrind: http://kcachegrind.sourceforge.net
.. _kcachegrind-converters: http://packages.debian.org/en/stable/kcachegrind-converters
.. _kdesdk: http://websvn.kde.org/trunk/KDE/kdesdk/kcachegrind/converters/
.. _screenshots: http://images.google.fr/images?q=kcachegrind

Command line usage
==================

Upon installation you should have a `pyprof2calltree` script in your path::

  $ pyprof2calltree --help
  Usage: /usr/bin/pyprof2calltree [-k] [-o output_file_path] [-i input_file_path] [-r scriptfile [args]]

  Options:
    -h, --help            show this help message and exit
    -o OUTFILE, --outfile=OUTFILE
                          Save calltree stats to <outfile>
    -i INFILE, --infile=INFILE
                          Read python stats from <infile>
    -r SCRIPT, --run-script=SCRIPT
                          Name of the python script to run to collect profiling
                          data
    -k, --kcachegrind     Run the kcachegrind tool on the converted data


Python shell usage
==================

`pyprof2calltree` is also best used from an interactive python shell such as
the default shell. For instance let us profile XML parsing::

  >>> from xml.etree import ElementTree
  >>> from cProfile import Profile
  >>> xml_content = '<a>\n' + '\t<b/><c><d>text</d></c>\n' * 100 + '</a>'
  >>> profiler = Profile()
  >>> profiler.runctx(
  ...     "ElementTree.fromstring(xml_content)",
  ...     locals(), globals())

  >>> from pyprof2calltree import convert, visualize
  >>> visualize(profiler.getstats())                            # run kcachegrind
  >>> convert(profiler.getstats(), 'profiling_results.kgrind')  # save for later

or with the ipython_::

  In [1]: %doctest_mode
  Exception reporting mode: Plain
  Doctest mode is: ON

  >>> from xml.etree import ElementTree
  >>> xml_content = '<a>\n' + '\t<b/><c><d>text</d></c>\n' * 100 + '</a>'
  >>> %prun -D out.stats ElementTree.fromstring(xml_content)

  *** Profile stats marshalled to file 'out.stats'

  >>> from pyprof2calltree import convert, visualize
  >>> visualize('out.stats')
  >>> convert('out.stats', 'out.kgrind')

  >>> results = %prun -r ElementTree.fromstring(xml_content)
  >>> visualize(results)

.. _ipython: http://ipython.scipy.org


Change log
==========

 - 1.4.0 - 2016-09-03: Support multiple functions with the same name, tick unit from millis to nanos, tests added (#15)
 - 1.3.2 - 2014-07-05: Bugfix: correct source file paths (#12)
 - 1.3.1 - 2013-11-27: Bugfix for broken output writing on python 3 (#8)
 - 1.3.0 - 2013-11-19: qcachegrind support
 - 1.2.0 - 2013-11-09: Python 3 support
 - 1.1.1 - 2013-09-25: Miscellaneous bugfixes
 - 1.1.0 - 2008-12-21: integrate fix in conversion by David Glick
 - 1.0.3 - 2008-10-16: fix typos in 1.0 release
 - 1.0 - 2008-10-16: initial release under the pyprof2calltree name

