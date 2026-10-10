import unittest
from pg1277_private_export_counter import coordinates


class StableClassCounterTest(unittest.TestCase):
    def test_expected_total_and_monotonic_diagnostic_not_formal(self):
        expected={k:{'missed':2,'covered':3}for k in ['LINE','METHOD','CLASS','BRANCH']}
        raw=('<report>'+''.join('<counter type="'+k+'" missed="1" covered="4"/>'for k in expected)+'</report>').encode()
        self.assertEqual(coordinates(raw,expected),[])
        for bad in [raw.replace(b'covered="4"',b'covered="5"'),raw.replace(b'missed="1" covered="4"',b'missed="3" covered="2"')]:
            with self.assertRaises(ValueError):coordinates(bad,expected)


if __name__=='__main__':unittest.main()
