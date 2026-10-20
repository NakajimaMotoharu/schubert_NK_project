import unittest
from pg5850_protocol_expression_public import four100


class NonVacuousExpressionCoverageTest(unittest.TestCase):
    def test_requires_six_complete_nonempty_actual_targets(self):
        counters={str(i):{k:{'covered':2,'missed':0}for k in('LINE','METHOD','CLASS','BRANCH')}for i in range(6)}
        self.assertTrue(four100(counters));self.assertFalse(four100({}))
        for key in('LINE','METHOD','CLASS','BRANCH'):
            altered={**counters,'0':{**counters['0'],key:{'covered':2,'missed':1}}}
            self.assertFalse(four100(altered))
            if key!='BRANCH':
                altered['0'][key]={'covered':0,'missed':0};self.assertFalse(four100(altered))


if __name__=='__main__':unittest.main()
