import ast
import unittest
from pg1303_current_candidate_ro_independent_post import payload


class CandidateRoIndependentPostTest(unittest.TestCase):
    def test_current_preservation_correct_complete_and_host_ro_actual(self):
        code=payload();ast.parse(code)
        self.assertIn("stage_root=base/'pg1300-unused-stage-v1'",code)
        self.assertIn('candidateReadOnlyVerified=true\\n',code)
        self.assertNotIn('unusedCandidatePlaced=true\\n',code)
        self.assertIn("t[5]=='ro,relatime'",code)
        self.assertIn('candidateBindMountMatchesRootAndNoNested=True',code)
        self.assertIn('json.loads(stage_before)==json.loads(stage_after)==after',code)
        self.assertNotIn('StartUnit',code)
        self.assertNotIn('StopUnit',code)


if __name__=='__main__':unittest.main()
