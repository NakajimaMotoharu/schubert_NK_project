import unittest
from pg5824_static3955_join import qualification_source


class Original3955LocalBindingTest(unittest.TestCase):
    def test_exact_current_and_genuine_terminal_before_any_join(self):
        raw=qualification_source()
        self.assertIn('PG5808-current3955-cases',raw)
        self.assertIn('pg5814-rollback-qualified-v1',raw)
        self.assertIn('(3955, 587, 1665)',raw)
        self.assertIn('originalReturnedManifestSha256',raw)
        self.assertNotIn('pg5782',raw)


if __name__=='__main__':unittest.main()
