Overview
========

Script to help visualize profiling data collected with the cProfile
python module with the `kcachegrind`_ graphical calltree analyser.

This is a rebranding of the venerable
http://www.gnome.org/~johan/lsprofcalltree.py script by David Allouche
et Al. to make it easier to distribute on pypi and behave more like the
scripts of the debian `kcachegrind-converters package`_. The final goal
is to make it part of the official upstream `kdesdk`_ package.

.. _`kcachegrind`: http://kcachegrind.sourceforge.net
.. _`kcachegrind-converters package`: http://packages.debian.org/en/stable/kcachegrind-converters
.. _`kdesdk`: http://websvn.kde.org/trunk/KDE/kdesdk/kcachegrind/converters/


Authors
=======

- David Allouche (initial author)
- Jp Calderone & Itamar Shtull-Trauring
- Johan Dahlin
- Olivier Grisel (repackaging)


Command line usage
==================

Upon installation you shoould have a `pyprof2calltree` script in your path::

  $ pyprof2calltree --help

TODO


Python shell usage
==================

pyprof2calltree is also best used from an interactive python shell such as
ipython_::

  TODO

.. _ipython: http://ipython.scipy.org

Change log
==========

 - 1.0 - 2008-10-16: initial release under the pyprof2calltree name

