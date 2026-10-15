import ast
import unittest

import pg3440_current_outbox_unused_post as current


class IndependentUnusedPost(unittest.TestCase):
    def test_current_reader_and_full_candidate_guards_without_reissue(self):
        raw = current.payload(); ast.parse(raw)
        for marker in [current.role.CURRENT, current.role.SOURCE, current.role.BOM,
                       current.role.BEFORE, current.role.SAVE, current.SLOT,
                       "len(c['artifacts'])==187", "len(c['migrations'])==29",
                       "require(native==after['native'])", 'pg3432-current-a9-before-view-v2/before.private.json',
                       'allClientAdvisoryFlock0', 'currentEpochApprovalUnchanged']:
            self.assertIn(marker, raw)
        for old in ['0.1.0-PG1638', 'pg1684-completed-unused-placement-v4']:
            self.assertNotIn(old, raw)
        self.assertIn('candidateNativeCredit', raw)


if __name__ == '__main__':
    unittest.main()
