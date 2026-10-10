import ast
import unittest
from pg1297_unused_candidate_independent_post import payload


class UnusedCandidatePostTest(unittest.TestCase):
    def test_old_scope_complete_literal_and_exact_unused_candidate_inventory(self):
        code=payload();ast.parse(code)
        self.assertIn("json.loads(stage_before)==json.loads(stage_after)==after",code)
        self.assertIn("len(value['artifacts'])==187",code)
        self.assertIn("(0,0,0o400,1,64)",code)
        self.assertIn('candidateNotCurrent=True',code)
        self.assertNotIn('StartUnit',code)
        self.assertNotIn('StopUnit',code)
        self.assertNotIn('os.rename',code)
        self.assertNotIn('os.symlink',code)


if __name__=='__main__':unittest.main()
