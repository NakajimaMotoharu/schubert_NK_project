import unittest
from pg1315_ordinary_publication_independent_post import payload


class IndependentPublicationPostTest(unittest.TestCase):
    def test_complete_payload_rebinds_only_signed_current_and_finite_startup(self):
        code=payload();compile(code,'<full independent post>','exec')
        self.assertIn('0.1.0-PG1292',code);self.assertNotIn('0.1.0-PG1068',code)
        self.assertIn("pub_before==after",code)
        self.assertIn("if k!='startup'",code)
        self.assertIn("finite.verify(fixed,public_now,'release'",code)
        self.assertIn('finite.verify_retained',code)
        self.assertIn('canonicalEpochWrites=1',code)
        self.assertIn("len(rows)==24",code)
        self.assertIn("lines[-2:]==[b'0',b'0']",code)
        self.assertIn('manager.UnrefUnit',code)
        self.assertNotIn('invalidate(',code)


if __name__=='__main__':unittest.main()
