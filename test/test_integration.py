import cProfile
import pstats
import sys
import unittest

from pyprof2calltree import CalltreeConverter

from .profile_code import expected_output_py2, expected_output_py3, top

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

if sys.version_info < (3, 0):
    expected_output = expected_output_py2
else:
    expected_output = expected_output_py3


class MockTimeProfile(cProfile.Profile):
    def __init__(self):
        self._mock_time = 0
        super(MockTimeProfile, self).__init__(self._timer, 1e-9)

    def _timer(self):
        now = self._mock_time
        self._mock_time += 1000
        return now


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.profile = MockTimeProfile()
        self.profile.enable()
        top()
        self.profile.disable()

    def test_direct_entries(self):
        entries = self.profile.getstats()
        converter = CalltreeConverter(entries)
        out_file = StringIO()

        converter.output(out_file)
        self.assertEqual(out_file.getvalue(), expected_output)

    def test_pstats_data(self):
        stats = pstats.Stats(self.profile)
        converter = CalltreeConverter(stats)
        out_file = StringIO()

        converter.output(out_file)
        self.assertEqual(out_file.getvalue(), expected_output)
