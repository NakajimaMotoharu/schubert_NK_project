import unittest
from pg1459_server_six import complete_result


class FullGateTest(unittest.TestCase):
    def test_all_exact_independent_totals_only(self):
        self.assertTrue(complete_result(0,True,[],3576,523,1635))
        baseline=[0,True,[],3576,523,1635]
        mutations={0:[None,True,1,143],1:[None,False,1],2:[None,['flaky'],['missingXML']],3:[None,True,3569,3575,3577],4:[None,True,522,524],5:[None,True,1634,1636]}
        for position,values in mutations.items():
            for value in values:
                changed=list(baseline);changed[position]=value
                with self.subTest(position=position,value=value):self.assertFalse(complete_result(*changed))


if __name__=='__main__':unittest.main()
