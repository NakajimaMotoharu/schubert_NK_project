import ast
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg1257_fresh_independent_terminal_post as schema
import pg2566_strict_current_backup_content as backup
from pg1446_current_cold_stage import W


class FreshBackupContent(unittest.TestCase):
    def setUp(self):
        receipt = json.loads((W / 'pg2560-strict-current-owned-post-v1/manifest.safe.json').read_bytes())
        self.seals = {n: receipt['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}

    def test_exact_actual_generation_whole_post_and_independent_content_oracle(self):
        raw = backup.payload(self.seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="actual"\n' + raw, '<fresh Backup fixture>'))
        for marker in ['b29fb3e5-2c46-4eac-b8f3-d03b986338e3', '2026-10-14T00:36:06.976135Z',
                       '0.1.0-PG2512/config/templates/api.yml', 'pg2554-native-stop-v1',
                       'independentCurrentRunBackupSummary', 'pg_restore', 'restorePruneAccepted=False']:
            self.assertIn(marker, raw)
        for marker in ['06236d14-a6f8-4d05-a6ff-49c713cc2647', '0.1.0-PG2428/config/templates/api.yml']:
            self.assertNotIn(marker, raw)
        forbidden = {'start', 'stop', 'restart', 'reload', 'daemon-reload', 'reset-failed'}
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n, ast.List):
                self.assertFalse(forbidden & {v.value for v in n.elts if isinstance(v, ast.Constant) and isinstance(v.value, str)})
        self.assertEqual('a79b45b5858a186fa82bec1ff36882271ab996a4', backup.entry().__globals__['SOURCE'])

    def test_missing_oracle_and_missing_seals_fail_before_guest_operation(self):
        with patch.object(backup.previous, 'payload', return_value='x=1'):
            with self.assertRaises(ValueError):
                backup.payload(self.seals)
        with self.assertRaises(ValueError):
            backup.payload({})


if __name__ == '__main__':
    unittest.main()
