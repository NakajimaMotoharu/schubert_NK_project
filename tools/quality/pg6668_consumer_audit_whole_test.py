import unittest
from unittest.mock import patch
import pg6668_consumer_audit_whole as p
import pg6670_original4170_artifacts as q


class GroupedOriginalDefinitionTest(unittest.TestCase):
    def test_exact_current_all_source_inventory_and_new_case_identity(self):
        declaration=p.declared_inventory()
        self.assertIsNotNone(declaration)
        added=q.new_case_identities('HEAD')
        self.assertEqual(12,len(added))
        self.assertEqual(3,len({(r['module'],r['class']) for r in added}))

    def test_original_reader_explicit_dimensions_without_replay(self):
        raw=q.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6670-original4170-v1')
        self.assertIn("('PG6668', (4170, 638, 1667), 6)",raw)
        self.assertNotIn('mvn ',raw)

    def test_missing_original77_cannot_start_whole(self):
        with patch.object(p.subprocess,'check_output',return_value=b''),patch.object(p,'QSHA',None):
            with self.assertRaisesRegex(ValueError,'freeze actual original77'):p.prerequisites('fixture')


if __name__=='__main__':unittest.main()
