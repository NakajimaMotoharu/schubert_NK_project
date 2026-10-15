import ast
import unittest

import pg3448_current_outbox_ro_post as post


class IndependentRoOracle(unittest.TestCase):
    def test_complete_actual_ro_namespace_and_preserved_native(self):
        raw = post.payload()
        ast.parse(raw)
        for marker in ['candidateReadOnlyVerified=true', 'candidateHostReadonlyVerified',
                       '/proc/1/ns/mnt', 'findmnt', "'ro'in mounts and 'rw'not in mounts",
                       '0.1.0-PG3420', post.role.SAVE, post.SLOT,
                       "require(native==after['native'])", 'pg3432-current-a9-before-view-v2']:
            self.assertIn(marker, raw)
        self.assertNotIn('unusedCandidatePlaced=true', raw)
        self.assertNotIn('PG2654', raw)


if __name__ == '__main__':
    unittest.main()
