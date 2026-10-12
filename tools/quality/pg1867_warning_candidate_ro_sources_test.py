"""Exact current/new release roles, WARNING identity and RO-only capabilities."""
import unittest
from pg1867_warning_candidate_ro_sources import sources,CANDIDATE,OLD,TOOLS,SAVE


class Ro(unittest.TestCase):
    def test_actual_emitted_oldwarning_newread_only_and_real_inputclass(self):
        s=sources('b'*64,'c'*64);java=s['Pg1867CandidateRo.java']
        self.assertIn(CANDIDATE,java);self.assertIn(OLD,java)
        self.assertIn('0.1.0-PG1846',java);self.assertIn('0.1.0-PG1638',java)
        self.assertIn('Outcome.WARNING',java);self.assertIn('candidateReadOnlyVerified=true',java)
        self.assertIn('pg1867_input_preflight.py',s)
        self.assertIn('Pg1867CurrentIdentityTest.java',s);self.assertIn('Pg1867InputBoundaryTest.java',s)
        ref=s['pg1867_native_refs.py'];self.assertIn('qualify_warning_parent(parent)',ref)
        self.assertIn('candidate_ro_post(candidate_before)',ref)
        self.assertNotIn('def place_candidate',ref);self.assertNotIn('StartUnit',ref)
        self.assertIn(TOOLS,java);self.assertIn(SAVE,java)
        for body in s.values():self.assertNotIn('pg1867-warning-unused-tools-v1',body)


if __name__=='__main__':unittest.main()
