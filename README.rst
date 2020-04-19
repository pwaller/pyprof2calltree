Overview
========

Script to help visualize profiling data collected with the cProfile
Python module with the kcachegrind_ (screenshots_) graphical calltree
analyser.

This is a rebranding of the venerable
http://www.gnome.org/~johan/lsprofcalltree.py script by David Allouche
et Al. It aims at making it easier to distribute (e.g. through PyPI)
and behave more like the scripts of the debian kcachegrind-converters_
package. The final goal is to make it part of the official upstream
kdesdk_ package.

.. _kcachegrind: http://kcachegrind.sourceforge.net
.. _kcachegrind-converters: https://packages.debian.org/en/stable/kcachegrind-converters
.. _kdesdk: http://websvn.kde.org/trunk/KDE/kdesdk/kcachegrind/converters/
.. _screenshots: http://images.google.fr/images?q=kcachegrind

Command line usage
==================

Upon installation you should have a `pyprof2calltree` script in your path::

  $ pyprof2calltree --help
  usage: pyprof2calltree [-h] [-o output_file_path] [-i input_file_path] [-k]
                         [-r scriptfile [args ...]]

  optional arguments:
    -h, --help            show this help message and exit
    -o output_file_path, --outfile output_file_path
                          Save calltree stats to <outfile>
    -i input_file_path, --infile input_file_path
                          Read Python stats from <infile>
    -k, --kcachegrind     Run the kcachegrind tool on the converted data
    -r scriptfile [args ...], --run-script scriptfile [args ...]
                          Name of the Python script to run to collect profiling
                          data


Python shell usage
==================

`pyprof2calltree` is also best used from an interactive Python shell such as
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

.. _ipython: https://ipython.org/


Change log
==========

 - 1.4.5 - 2020-04-19: Nothing user facing - changes to testing and remove deprecated eggecutable
 - 1.4.4 - 2018-10-19: Numerous small improvements, drop support for EOL python versions
 - 1.4.3 - 2017-07-28: Windows support (fixed is_installed check - #21)
 - 1.4.2 - 2017-07-19: No feature or bug fixes, just license clarification (#20)
 - 1.4.1 - 2017-05-20: No feature or bug fixes, just test distribution (#17)
 - 1.4.0 - 2016-09-03: Support multiple functions with the same name, tick unit from millis to nanos, tests added (#15)
 - 1.3.2 - 2014-07-05: Bugfix: correct source file paths (#12)
 - 1.3.1 - 2013-11-27: Bugfix for broken output writing on Python 3 (#8)
 - 1.3.0 - 2013-11-19: qcachegrind support
 - 1.2.0 - 2013-11-09: Python 3 support
 - 1.1.1 - 2013-09-25: Miscellaneous bugfixes
 - 1.1.0 - 2008-12-21: integrate fix in conversion by David Glick
 - 1.0.3 - 2008-10-16: fix typos in 1.0 release
 - 1.0 - 2008-10-16: initial release under the pyprof2calltree name
