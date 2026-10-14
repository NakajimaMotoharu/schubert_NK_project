import ast
import unittest
from pg2552_strict_current_parent_projection import payload
from pg2516_current_strict_candidate_sources import SOURCE


class NewParentProjection(unittest.TestCase):
    def test_complete_source_bom_whole_seal_and_eighteen_typed_fields(self):
        raw = payload('a'*64, '2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f')
        ast.parse(raw)
        for marker in [SOURCE, 'pg2548-strict-current-full-seal-v1', "before['manifestSha256']==BOM",
                       'len(fields)==18', "type(v)is str", "fields['Id']=='schubert-nk-morning-controller.service'"]:
            self.assertIn(marker, raw)
        self.assertNotIn("SOURCE='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'", raw)
        self.assertNotIn('pg2456-question-current-full-seal-v1', raw)


if __name__ == '__main__':
    unittest.main()
