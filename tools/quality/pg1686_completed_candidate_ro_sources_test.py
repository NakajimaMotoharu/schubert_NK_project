"""Independent current/candidate identity scopes and no re-placement capability."""
import unittest
from pyflakes.api import check
import pg1686_completed_candidate_ro_sources as p


class CompletedRoSourceTest(unittest.TestCase):
    def test_candidate_and_restore_are_distinct_and_final(self):
        raw=p.method()
        self.assertEqual(1,raw.count('verifyCurrentIdentity();'))
        self.assertIn('LABEL="PG1638";Pg387TrustedDeployment.STEM="pg1638";',raw)
        self.assertIn('LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544";',raw)
        self.assertLess(raw.index('candidate=Pg387TrustedDeployment.verify()'),raw.index('LABEL="PG1544"'))
        self.assertLess(raw.index('LABEL="PG1544"'),raw.index('verifyCurrentIdentity();'))
        for old in ['PG1292','PG1068','769ddb15','d5b0010']:self.assertNotIn(old,raw)

    def test_exact_completed_profile_no_archive_or_replacement(self):
        generated=p.sources();java=generated['Pg1686CandidateRo.java'];refs=generated['pg1686_native_refs.py']
        self.assertIn('candidateReadOnly();refs.check("ro");',java)
        self.assertIn('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a',java)
        self.assertIn('d28eead2-941c-4b97-9747-1758c0809e29',java)
        self.assertIn('verifyCurrentIdentity();var approval=Pg387TrustedDeployment.verify();',java)
        self.assertIn('candidateReadOnlyVerified=true',java)
        for old in ['place_candidate','tar.extractall','archive=stage','PG1292','PG1068']:self.assertNotIn(old,refs)
        self.assertIn('candidate_ro_post(candidate_before)',refs)
        self.assertIn('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',refs)
        self.assertIn('pg1686_native_owned_stop',refs)
        self.assertLess(java.index('beforeOwnership(Pg1686CandidateRo::verifyInputClosure)'),java.index('require(MaintenanceFileLock.create()'))
        for name,raw in generated.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<completed candidate RO '+name+'>'))


if __name__=='__main__':unittest.main()
