#!/usr/bin/env python
# Copyright (c) 2006-2008, David Allouche, Jp Calderone, Itamar Shtull-Trauring,
# Johan Dahlin, Olivier Grisel <olivier.grisel@ensta.org>
#
# Send maintenance requests needing new pypi packages to:
#   Peter Waller <p@pwaller.net>
#   https://github.com/pwaller/pyprof2calltree
#
# See CONTRIBUTORS.txt.
#
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""pyprof2calltree: profiling output which is readable by kcachegrind

This script can either take raw cProfile.Profile.getstats() log entries or
take a previously recorded instance of the pstats.Stats class.
"""

import cProfile
import optparse
import os
import pstats
import subprocess
import sys
import tempfile

__all__ = ['convert', 'visualize', 'CalltreeConverter']

class Code(object):
    pass

class Entry(object):
    pass

def is_basestring(s):
    try:
        u = unicode
        # Python 2.x
        return isinstance(s, basestring)
    except NameError:
        # Python 3.x
        return isinstance(s, (str, bytes))


def pstats2entries(data):
    """Helper to convert serialized pstats back to a list of raw entries

    Converse operation of cProfile.Profile.snapshot_stats()
    """
    entries = dict()
    allcallers = dict()

    # first pass over stats to build the list of entry instances
    for code_info, call_info in list(data.stats.items()):
        # build a fake code object
        code = Code()
        code.co_filename, code.co_firstlineno, code.co_name = code_info

        # build a fake entry object
        cc, nc, tt, ct, callers = call_info
        entry = Entry()
        entry.code = code
        entry.callcount = cc
        entry.reccallcount = nc - cc
        entry.inlinetime = tt
        entry.totaltime = ct

        # to be filled during the second pass over stats
        entry.calls = list()

        # collect the new entry
        entries[code_info] = entry
        allcallers[code_info] = list(callers.items())

    # second pass of stats to plug callees into callers
    for entry in entries.values():
        entry_label = cProfile.label(entry.code)
        entry_callers = allcallers.get(entry_label, [])
        for entry_caller, call_info in entry_callers:
            entries[entry_caller].calls.append((entry, call_info))

    return list(entries.values())


def is_installed(prog):
    """Return whether or not a given executable is installed on the machine."""
    devnull = open(os.devnull, 'w')
    retcode = subprocess.call(['which', prog], stdout=devnull)
    devnull.close()
    return retcode == 0


KCACHEGRIND_EXECUTABLES = ["kcachegrind", "qcachegrind"]

class CalltreeConverter(object):
    """Convert raw cProfile or pstats data to the calltree format"""

    def __init__(self, profiling_data):
        if is_basestring(profiling_data):
            # treat profiling_data as a filename of pstats serialized data
            self.entries = pstats2entries(pstats.Stats(profiling_data))
        elif isinstance(profiling_data, pstats.Stats):
            # convert pstats data to cProfile list of entries
            self.entries = pstats2entries(profiling_data)
        else:
            # assume this are direct cProfile entries
            self.entries = profiling_data
        self.out_file = None

    def output(self, out_file):
        """Write the converted entries to out_file"""
        self.out_file = out_file
        out_file.write('events: Ticks\n')
        self._print_summary()
        for entry in self.entries:
            self._entry(entry)

    def visualize(self):
        """Launch kcachegrind on the converted entries.

        One of the executables listed in KCACHEGRIND_EXECUTABLES
        must be present in the system path.
        """

        if self.out_file is None:
            _, outfile = tempfile.mkstemp(".log", "pyprof2calltree")
            f = open(outfile, "w")
            self.output(f)
            use_temp_file = True
        else:
            use_temp_file = False

        available_cmd = None

        for cmd in KCACHEGRIND_EXECUTABLES:
            if is_installed(cmd):
                available_cmd = cmd
                break

        if available_cmd is None:
            sys.stderr.write("Could not find kcachegrind. Tried: %s\n" %
                    ", ".join(KCACHEGRIND_EXECUTABLES))
            return

        self.out_file.close()

        try:
            subprocess.call([cmd, self.out_file.name])
        finally:
            # clean the temporary file
            if use_temp_file:
                os.remove(outfile)
                self.out_file = None

    def _print_summary(self):
        max_cost = 0
        for entry in self.entries:
            totaltime = int(entry.totaltime * 1000)
            max_cost = max(max_cost, totaltime)
        self.out_file.write('summary: %d\n' % (max_cost,))

    def _entry(self, entry):
        out_file = self.out_file

        code = entry.code

        co_filename, co_firstlineno, co_name = cProfile.label(code)
        if co_filename != '~' and co_firstlineno != 0:
            out_file.write('fl=%s\nfn=%s\n' % (
                co_filename, co_name))
        else:
            out_file.write('fn=%s\n' % co_name)

        inlinetime = int(entry.inlinetime * 1000)
        if is_basestring(code):
            out_file.write('0  %s\n' % inlinetime)
        else:
            out_file.write('%d %d\n' % (code.co_firstlineno, inlinetime))

        # recursive calls are counted in entry.calls
        if entry.calls:
            calls = entry.calls
        else:
            calls = []

        if is_basestring(code):
            lineno = 0
        else:
            lineno = code.co_firstlineno

        for subentry, call_info in calls:
            self._subentry(lineno, subentry, call_info)
        out_file.write('\n')

    def _subentry(self, lineno, subentry, call_info):
        out_file = self.out_file
        code = subentry.code
        co_filename, co_firstlineno, co_name = cProfile.label(code)
        if co_filename != '~' and co_firstlineno != 0:
            out_file.write('cfl=%s\ncfn=%s\n' %
                (co_filename, co_name))
        else:
            out_file.write('cfn=%s\n' % co_name)
        out_file.write('calls=%d %d\n' % (call_info[0], co_firstlineno))

        totaltime = int(call_info[3] * 1000)
        out_file.write('%d %d\n' % (lineno, totaltime))

def main():
    """Execute the converter using parameters provided on the command line"""

    usage = ("%s [-k] [-o output_file_path] [-i input_file_path]"
             " [-r scriptfile [args]]")
    parser = optparse.OptionParser(usage=usage % sys.argv[0])
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest="outfile",
                      help="Save calltree stats to <outfile>", default=None)
    parser.add_option('-i', '--infile', dest="infile",
                      help="Read python stats from <infile>", default=None)
    parser.add_option('-r', '--run-script', dest="script",
                      help="Name of the python script to run to collect"
                      " profiling data", default=None)
    parser.add_option('-k', '--kcachegrind', dest="kcachegrind",
                      help="Run the kcachegrind tool on the converted data",
                      action="store_true")
    options, args = parser.parse_args()


    outfile = options.outfile

    if options.script is not None:
        # collect profiling data by running the given script

        sys.argv[:] = [options.script] + args
        if not options.outfile:
            outfile = '%s.log' % os.path.basename(options.script)

        prof = cProfile.Profile()

        # Try to deal with programs (e.g., bzr) that avoid sys.exit(),
        # but still run atexit handlers.
        import atexit
        atexit.register(exit)

        try:
            try:
                prof = prof.run('execfile(%r)' % (sys.argv[0],))
            except SystemExit:
                pass
        finally:
            kg = CalltreeConverter(pstats.Stats(prof))

    elif options.infile is not None:
        # use the profiling data from some input file
        if not options.outfile:
            outfile = '%s.log' % os.path.basename(options.infile)

        if options.infile == outfile:
            # prevent name collisions by appending another extension
            outfile += ".log"

        kg = CalltreeConverter(pstats.Stats(options.infile))

    else:
        # at least an input file or a script to run is required
        parser.print_usage()
        sys.exit(2)

    if options.outfile is not None or not options.kcachegrind:
        # user either explicitly required output file or requested by not
        # explicitly asking to launch kcachegrind
        sys.stderr.write("writing converted data to: %s\n" % outfile)
        kg.output(open(outfile, 'w'))

    if options.kcachegrind:
        sys.stderr.write("launching kcachegrind\n")
        kg.visualize()


def visualize(profiling_data):
    """launch the kcachegrind on `profiling_data`

    `profiling_data` can either be:
        - a pstats.Stats instance
        - the filename of a pstats.Stats dump
        - the result of a call to cProfile.Profile.getstats()
    """
    converter = CalltreeConverter(profiling_data)
    converter.visualize()

def convert(profiling_data, outputfile):
    """convert `profiling_data` to calltree format and dump it to `outputfile`

    `profiling_data` can either be:
        - a pstats.Stats instance
        - the filename of a pstats.Stats dump
        - the result of a call to cProfile.Profile.getstats()

    `outputfile` can either be:
        - a file() instance open in write mode
        - a filename
    """
    converter = CalltreeConverter(profiling_data)
    if is_basestring(outputfile):
        f = open(outputfile, "w")
        try:
            converter.output(f)
        finally:
            f.close()
    else:
        converter.output(outputfile)


if __name__ == '__main__':
    sys.exit(main())
