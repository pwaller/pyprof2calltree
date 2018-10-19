#!/usr/bin/env python
# Copyright (c) 2006-2008, David Allouche, Jp Calderone, Itamar Shtull-Trauring,
# Johan Dahlin, Olivier Grisel <olivier.grisel@ensta.org>
#
# Send maintenance requests needing new PyPI packages to:
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

from __future__ import unicode_literals

import argparse
import cProfile
import errno
import io
import os
import pstats
import subprocess
import sys
import tempfile
from collections import defaultdict

__all__ = ['convert', 'visualize', 'CalltreeConverter']

SCALE = 1e9


class Code(object):
    def __init__(self, filename, firstlineno, name):
        self.co_filename = filename
        self.co_firstlineno = firstlineno
        self.co_name = name

    def __repr__(self):
        return '<Code: %s, %s, %s>' % (self.co_filename, self.co_firstlineno,
                                       self.co_name)


class Entry(object):
    def __init__(self, code, callcount, reccallcount, inlinetime, totaltime, calls):
        self.code = code
        self.callcount = callcount
        self.reccallcount = reccallcount
        self.inlinetime = inlinetime
        self.totaltime = totaltime
        self.calls = calls

    def __repr__(self):
        return '<Entry: %s, %s, %s, %s, %s, %s>' % (
            self.code, self.callcount, self.reccallcount, self.inlinetime,
            self.totaltime, self.calls
        )


class Subentry(object):
    def __init__(self, code, callcount, reccallcount, inlinetime, totaltime):
        self.code = code
        self.callcount = callcount
        self.reccallcount = reccallcount
        self.inlinetime = inlinetime
        self.totaltime = totaltime

    def __repr__(self):
        return '<Subentry: %s, %s, %s, %s, %s>' % (
            self.code, self.callcount, self.reccallcount, self.inlinetime,
            self.totaltime
        )


def is_basestring(s):
    try:
        unicode
        # Python 2.x
        return isinstance(s, basestring)
    except NameError:
        # Python 3.x
        return isinstance(s, (str, bytes))


def pstats2entries(data):
    """Helper to convert serialized pstats back to a list of raw entries.

    Converse operation of cProfile.Profile.snapshot_stats()
    """
    # Each entry's key is a tuple of (filename, line number, function name)
    entries = {}
    allcallers = {}

    # first pass over stats to build the list of entry instances
    for code_info, call_info in data.stats.items():
        # build a fake code object
        code = Code(*code_info)

        # build a fake entry object.  entry.calls will be filled during the
        # second pass over stats
        cc, nc, tt, ct, callers = call_info
        entry = Entry(code, callcount=cc, reccallcount=nc - cc, inlinetime=tt,
                      totaltime=ct, calls=[])

        # collect the new entry
        entries[code_info] = entry
        allcallers[code_info] = list(callers.items())

    # second pass of stats to plug callees into callers
    for entry in entries.values():
        entry_label = cProfile.label(entry.code)
        entry_callers = allcallers.get(entry_label, [])
        for entry_caller, call_info in entry_callers:
            cc, nc, tt, ct = call_info
            subentry = Subentry(entry.code, callcount=cc, reccallcount=nc - cc,
                                inlinetime=tt, totaltime=ct)
            # entry_caller has the same form as code_info
            entries[entry_caller].calls.append(subentry)

    return list(entries.values())


def is_installed(prog):
    """Return whether or not a given executable is installed on the machine."""
    with open(os.devnull, 'w') as devnull:
        try:
            if os.name == 'nt':
                retcode = subprocess.call(['where', prog], stdout=devnull)
            else:
                retcode = subprocess.call(['which', prog], stdout=devnull)
        except OSError as e:
            # If where or which doesn't exist, a "ENOENT" error will occur (The
            # FileNotFoundError subclass on Python 3).
            if e.errno != errno.ENOENT:
                raise
            retcode = 1

    return retcode == 0


def _entry_sort_key(entry):
    return cProfile.label(entry.code)


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
        self._code_by_position = defaultdict(set)
        self._populate_code_by_position()

    def _populate_code_by_position(self):
        for entry in self.entries:
            self._add_code_by_position(entry.code)
            if not entry.calls:
                continue
            for subentry in entry.calls:
                self._add_code_by_position(subentry.code)

    def _add_code_by_position(self, code):
        co_filename, _, co_name = cProfile.label(code)
        self._code_by_position[(co_filename, co_name)].add(code)

    def munged_function_name(self, code):
        co_filename, co_firstlineno, co_name = cProfile.label(code)
        if len(self._code_by_position[(co_filename, co_name)]) == 1:
            return co_name
        return "%s:%d" % (co_name, co_firstlineno)

    def output(self, out_file):
        """Write the converted entries to out_file"""
        self.out_file = out_file
        out_file.write('event: ns : Nanoseconds\n')
        out_file.write('events: ns\n')
        self._output_summary()
        for entry in sorted(self.entries, key=_entry_sort_key):
            self._output_entry(entry)

    def visualize(self):
        """Launch kcachegrind on the converted entries.

        One of the executables listed in KCACHEGRIND_EXECUTABLES
        must be present in the system path.
        """

        available_cmd = None
        for cmd in KCACHEGRIND_EXECUTABLES:
            if is_installed(cmd):
                available_cmd = cmd
                break

        if available_cmd is None:
            sys.stderr.write("Could not find kcachegrind. Tried: %s\n" %
                             ", ".join(KCACHEGRIND_EXECUTABLES))
            return

        if self.out_file is None:
            fd, outfile = tempfile.mkstemp(".log", "pyprof2calltree")
            use_temp_file = True
        else:
            outfile = self.out_file.name
            use_temp_file = False

        try:
            if use_temp_file:
                with io.open(fd, "w") as f:
                    self.output(f)
            subprocess.call([available_cmd, outfile])
        finally:
            # clean the temporary file
            if use_temp_file:
                os.remove(outfile)
                self.out_file = None

    def _output_summary(self):
        max_cost = 0
        for entry in self.entries:
            totaltime = int(entry.totaltime * SCALE)
            max_cost = max(max_cost, totaltime)
        # Version 0.7.4 of kcachegrind appears to ignore the summary line and
        # calculate the total cost by summing the exclusive cost of all
        # functions, but it doesn't hurt to output it anyway.
        self.out_file.write('summary: %d\n' % (max_cost,))

    def _output_entry(self, entry):
        out_file = self.out_file

        code = entry.code

        co_filename, co_firstlineno, co_name = cProfile.label(code)
        munged_name = self.munged_function_name(code)
        out_file.write('fl=%s\nfn=%s\n' % (co_filename, munged_name))

        inlinetime = int(entry.inlinetime * SCALE)
        out_file.write('%d %d\n' % (co_firstlineno, inlinetime))

        # recursive calls are counted in entry.calls
        if entry.calls:
            for subentry in sorted(entry.calls, key=_entry_sort_key):
                self._output_subentry(co_firstlineno, subentry.code,
                                      subentry.callcount,
                                      int(subentry.totaltime * SCALE))

        out_file.write('\n')

    def _output_subentry(self, lineno, code, callcount, totaltime):
        out_file = self.out_file
        co_filename, co_firstlineno, co_name = cProfile.label(code)
        munged_name = self.munged_function_name(code)
        out_file.write('cfl=%s\ncfn=%s\n' % (co_filename, munged_name))
        out_file.write('calls=%d %d\n' % (callcount, co_firstlineno))
        out_file.write('%d %d\n' % (lineno, totaltime))


def main():
    """Execute the converter using parameters provided on the command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', metavar='output_file_path',
                        help="Save calltree stats to <outfile>")
    parser.add_argument('-i', '--infile', metavar='input_file_path',
                        help="Read Python stats from <infile>")
    parser.add_argument('-k', '--kcachegrind',
                        help="Run the kcachegrind tool on the converted data",
                        action="store_true")
    parser.add_argument('-r', '--run-script',
                        nargs=argparse.REMAINDER,
                        metavar=('scriptfile', 'args'),
                        dest='script',
                        help="Name of the Python script to run to collect"
                        " profiling data")
    args = parser.parse_args()

    outfile = args.outfile

    if args.script is not None:
        # collect profiling data by running the given script
        if not args.outfile:
            outfile = '%s.log' % os.path.basename(args.script[0])

        fd, tmp_path = tempfile.mkstemp(suffix='.prof', prefix='pyprof2calltree')
        os.close(fd)
        try:
            cmd = [
                sys.executable,
                '-m', 'cProfile',
                '-o', tmp_path,
            ]
            cmd.extend(args.script)
            subprocess.check_call(cmd)

            kg = CalltreeConverter(tmp_path)
        finally:
            os.remove(tmp_path)

    elif args.infile is not None:
        # use the profiling data from some input file
        if not args.outfile:
            outfile = '%s.log' % os.path.basename(args.infile)

        if args.infile == outfile:
            # prevent name collisions by appending another extension
            outfile += ".log"

        kg = CalltreeConverter(pstats.Stats(args.infile))

    else:
        # at least an input file or a script to run is required
        parser.print_usage()
        sys.exit(2)

    if args.outfile is not None or not args.kcachegrind:
        # user either explicitly required output file or requested by not
        # explicitly asking to launch kcachegrind
        sys.stderr.write("writing converted data to: %s\n" % outfile)
        with open(outfile, 'w') as f:
            kg.output(f)

    if args.kcachegrind:
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
        with open(outputfile, "w") as f:
            converter.output(f)
    else:
        converter.output(outputfile)


if __name__ == '__main__':
    sys.exit(main())
