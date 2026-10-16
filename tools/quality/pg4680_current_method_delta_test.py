"""Strict matching denominators and zero means zero, not an assumed class-level gap."""
import unittest
from pyflakes.api import checkPath
import pg4680_current_method_delta as d


class MethodDelta(unittest.TestCase):
    def test_already_closed_and_actual_new_conditions(self):
        zero={'LINE':{'missed':0,'covered':11},'METHOD':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':14}}
        self.assertEqual({'LINE':0,'METHOD':0,'BRANCH':0},d.delta(zero,zero))
        old={'LINE':{'missed':9,'covered':0},'METHOD':{'missed':1,'covered':0}}
        new={'LINE':{'missed':0,'covered':9},'METHOD':{'missed':0,'covered':1}}
        self.assertEqual({'LINE':9,'METHOD':1,'BRANCH':0},d.delta(old,new))
        for invalid in [{'LINE':{'missed':False,'covered':9},'METHOD':new['METHOD']},{'LINE':{'missed':0,'covered':10},'METHOD':new['METHOD']},{'LINE':{'missed':1,'covered':8},'METHOD':new['METHOD']},{}]:
            with self.assertRaises(ValueError):d.delta(old,invalid)
        self.assertEqual(0,checkPath(d.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
