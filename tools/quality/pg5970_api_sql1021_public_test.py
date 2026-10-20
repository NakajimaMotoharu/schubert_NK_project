import unittest
import pg5970_api_sql1021_public as t


class ExactFourCounterQualificationTest(unittest.TestCase):
    def test_missing_branch_zero_method_missed_or_wrong_cardinality_never_pass(self):
        good = {str(i): {k: {'covered': 1, 'missed': 0} for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')} for i in range(16)}
        self.assertTrue(t.four100(good))
        for bad in ({**good, 'extra':good['0']}, {k:v for k,v in good.items() if k!='0'}, {**good, '0': {k:v for k,v in good['0'].items() if k!='BRANCH'}}, {**good, '0': {**good['0'], 'BRANCH': {'covered':0,'missed':0}}}, {**good, '0': {**good['0'], 'METHOD': {'covered':1,'missed':1}}}):
            self.assertFalse(t.four100(bad))


if __name__ == '__main__':
    unittest.main()
