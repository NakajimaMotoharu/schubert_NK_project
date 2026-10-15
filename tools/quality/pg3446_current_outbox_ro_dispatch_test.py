import ast
import unittest

import pg3446_current_outbox_ro_dispatch as current


class FullRoDispatchBoundary(unittest.TestCase):
    def test_standalone_stage_binds_current_boot_and_release(self):
        ast.parse(current.STAGE)
        self.assertIn(current.role.role.BOOT, current.STAGE)
        self.assertIn('0.1.0-PG2802', current.STAGE)
        self.assertIn(current.role.TOOLS, current.STAGE)
        self.assertNotIn(current.role.role.old.BOOT, current.STAGE)
        self.assertNotIn('PG2512', current.STAGE)

    def test_full_operator_source_and_independent_unused_post_required(self):
        raw = current.source()
        ast.parse(raw)
        for marker in [current.role.role.SOURCE, 'pg3444-frozen',
                       'pg3440-current-outbox-unused-independent-post-v1',
                       'pg3446-stage-v1.exit', 'prepare-ro']:
            self.assertIn(marker, raw)
        for marker in ['2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0',
                       'pg2667-frozen', 'pg2668-stage']:
            self.assertNotIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
