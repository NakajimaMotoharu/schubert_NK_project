import unittest
import pg5864_current3971_public as target


class Original3971ProjectionTest(unittest.TestCase):
    def test_exact_cases_read_only_and_explicit_four_design_ids(self):
        raw=target.payload({})
        self.assertIn('PG5860',raw);self.assertNotIn('PG5832',raw)
        self.assertNotIn('Popen',raw)
        operator=target.operator_source()
        self.assertIn('len(cases)!=3971',operator)
        self.assertIn('len(trace)!=4',operator)
        self.assertIn("'PT-JMS-TERM'",operator)
        self.assertIn("'formalAccepted':False",operator)
        self.assertNotIn("'BUG1494LimitedPolicyScopeVerified'",operator)


if __name__=='__main__':unittest.main()
