import unittest
from unittest.mock import patch
import pg6706_broker_cleanup_whole as p
import pg6708_original4184_artifacts as q


class GroupedBrokerDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_independent_additions(self):
        self.assertIsNotNone(p.declared_inventory())
        added=q.new_case_identities('HEAD')
        self.assertEqual(14,len(added))
        self.assertEqual(5,len({(r['module'],r['class']) for r in added}))

    def test_explicit_original_reader_dimensions_without_replay(self):
        raw=q.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6708-original4184-v1')
        self.assertIn("('PG6706', (4184, 643, 1667), 8)",raw)
        self.assertNotIn('mvn ',raw)

    def test_no_whole_without_genuine_original127(self):
        with patch.object(p.subprocess,'check_output',return_value=b''),patch.object(p,'QSHA',None):
            with self.assertRaisesRegex(ValueError,'freeze actual original127'):
                p.prerequisites('fixture')


if __name__=='__main__':unittest.main()
