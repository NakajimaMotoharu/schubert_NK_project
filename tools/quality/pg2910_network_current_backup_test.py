"""Complete current graph and independent literal Backup configuration oracle."""
import ast
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg1257_fresh_independent_terminal_post as schema
import pg2910_network_current_backup_content as p


class BackupContent(unittest.TestCase):
    def seals(self):
        post=json.loads((p.W/'pg2898-network-owned-post-v1/manifest.safe.json').read_bytes())
        return {n:post['proofHashes'][n]['sha256']for n in schema.previous.SEALS}

    def test_actual_graph_and_oracle_only_current_generation(self):
        raw=p.payload(self.seals())
        self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+raw,'<actual current complete Backup reader>'))
        for v in ['0dc63b79-3f9a-450c-b2a6-56f86272d272','2026-10-14T19:12:28.842213Z','0.1.0-PG2802/config/templates/api.yml',p.SLOT,'qualify_backup','ordinaryPgRestoreListExit=0','restorePruneAccepted=False']:
            self.assertTrue(v in raw,v)
        for v in ['b29fb3e5-2c46-4eac-b8f3-d03b986338e3','0.1.0-PG2512/config/templates/api.yml']:
            self.assertFalse(v in raw,v)
        forbidden={'start','stop','restart','reload','daemon-reload','reset-failed'}
        for node in ast.walk(ast.parse(raw)):
            if isinstance(node,ast.List):
                self.assertFalse(forbidden&{v.value for v in node.elts if isinstance(v,ast.Constant)and isinstance(v.value,str)})
        self.assertEqual(p.SOURCE,p.entry().__globals__['SOURCE'])

    def test_missing_content_or_seals_refused_before_execution(self):
        with patch.object(p.previous.previous,'payload',return_value='x=1'):
            with self.assertRaises(ValueError):p.payload(self.seals())
        with self.assertRaises(ValueError):p.payload({})


if __name__=='__main__':unittest.main()
