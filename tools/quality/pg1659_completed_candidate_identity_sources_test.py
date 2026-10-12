"""Verify actual current fourtuple gate call and independent null/foreign fixture."""
import unittest
import pg1659_completed_candidate_identity_sources as p
import pg1660_completed_candidate_compile_v3 as c


class CurrentIdentitySourceTest(unittest.TestCase):
    def test_actual_current_tuple_and_fixed_new_namespace(self):
        raw = p.sources('a' * 64)['Pg1640UnusedStage.java']
        self.assertIn('LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544"', raw)
        self.assertIn('verifyCurrentIdentity();var approval=Pg387TrustedDeployment.verify();', raw)
        for literal in ['"PG1544".equals(Pg387TrustedDeployment.LABEL)', '"pg1544".equals(Pg387TrustedDeployment.STEM)', '"4d6bcbddb417b76d27e52d5d9640752c300edccf".equals(Pg387TrustedDeployment.SOURCE)', 'Path.of("/opt/schubert-nk/releases/0.1.0-PG1544").equals(Pg387TrustedDeployment.RELEASE)']:
            self.assertIn(literal, raw)
        self.assertNotIn('LABEL="PG1292"', raw)
        self.assertIn('nullNpe0=true', p.TEST)
        self.assertIn('checks!=13', p.TEST)
        self.assertIn('Pg1660CurrentIdentityTest.java', c.compiler())
        self.assertIn("('identity','Pg1660CurrentIdentityTest')", c.compiler())
        refs = p.sources('a' * 64)['pg1640_native_refs.py']
        self.assertIn('/home/ubuntu/pg1661-candidate-input-v1', refs)
        self.assertIn('pg1662-completed-unused-placement-v3', refs)


if __name__ == '__main__':
    unittest.main()
