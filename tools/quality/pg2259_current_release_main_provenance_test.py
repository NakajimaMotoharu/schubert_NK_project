import unittest
from pyflakes.api import check
import pg2259_current_release_main_provenance as p


class CurrentMainBytes(unittest.TestCase):
    def test_whole_set_and_every_duplicate_physical_occurrence(self):
        expected={str(i):'a'*64 for i in range(1643)};actual={k:[v,v]for k,v in expected.items()}
        self.assertEqual({'mainClasses':1643,'physicalOccurrences':3286,'classByteMismatch':0},p.compare(expected,actual))
        for wrong in [None,{},dict(actual,foreign=['a'*64]),{k:[]for k in actual},{**actual,'1':['a'*64,'b'*64]}]:
            with self.assertRaises(ValueError):p.compare(expected,wrong)
        raw=p.payload(expected)
        self.assertEqual(0,check(raw,'<whole current signed Main reader>'))
        self.assertIn('0.1.0-PG2126',raw);self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
