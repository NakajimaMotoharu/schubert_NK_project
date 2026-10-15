import ast
import json
import unittest
import pg3482_outbox_current_a01 as current


class RealA01ExactGeneration(unittest.TestCase):
    def test_complete_same_root_guard_and_owned_socks(self):
        raw = current.code()
        ast.parse(raw)
        live = json.loads((current.W / current.LIVE / 'manifest.safe.json').read_bytes())
        for marker in [current.SOURCE, current.BOM, 'PG3420', 'pg3462', 'PG3482',
                       'pg3464-outbox-current-noargs-once-v1',
                       'pg3458-current-outbox-publication-independent-post-v1',
                       'pg3480-outbox-chr-socks-v1', str(live['rootPid']), live['binding']['invocation']]:
            self.assertTrue(marker in raw, marker)
        self.assertNotIn('pg2882-network-chr-socks-v1', raw)
        self.assertNotIn(current.old.SOURCE, raw)
        self.assertNotIn(current.old.BOM, raw)


if __name__ == '__main__':
    unittest.main()
