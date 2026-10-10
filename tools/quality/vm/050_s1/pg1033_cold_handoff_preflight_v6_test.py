import ast
import unittest
from pg1033_cold_handoff_preflight_v6 import payload
from pg1032_cold_handoff_preflight_v5 import missing_globals


class Trace(unittest.TestCase):
    def test_exact_public_private_profile_and_closed_function_set(self):
        raw = payload()
        tree = ast.parse(raw)
        self.assertEqual([], missing_globals(raw, ['snapshot', 'complete_configuration', 'read', 'actor', 'controls']))
        values = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertEqual(1, values.count('PG1033-cold-handoff-preflight-v6'))
        self.assertIn('/var/lib/pgpt-s1-preservation/pg1033-cold-handoff-preflight-v6', values)
        for old in ('PG1028-cold-handoff-preflight-v1', 'pg1032-cold-handoff-preflight-v5', 'PG1032_REFUSED'):
            self.assertNotIn(old, raw)
        self.assertNotIn('pidfd_send_signal(', raw)


if __name__ == '__main__': unittest.main()
