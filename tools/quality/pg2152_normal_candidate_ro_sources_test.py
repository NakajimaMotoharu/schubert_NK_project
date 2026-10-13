import unittest
from pg2152_normal_candidate_ro_sources import sources


class CandidateRo(unittest.TestCase):
    def test_actual_normal_current_and_candidate_roles(self):
        values=sources('a'*64)
        raw='\n'.join(values.values())
        self.assertIn('Pg2152CandidateRo.java',values)
        for literal in ['3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','0fd734195b4d5338f6b7e860e087cce561d49562','0.1.0-PG2126','0.1.0-PG1846','genuineParentNormalWarningOriginal=true','candidateReadOnlyVerified=true','PG2152_INPUT_CLOSURE_READY']:self.assertIn(literal,raw)
        self.assertNotIn('managerFailureRetained=true',raw)
        self.assertNotIn("'SuccessExitStatus': ''",raw)
        self.assertIn("'SuccessExitStatus': '10'",raw)
        self.assertNotIn('REGULAR_MORNING_UNIT_EXCHANGE',raw)
        self.assertNotIn('Pg2144UnusedStage',raw)


if __name__=='__main__':unittest.main()
