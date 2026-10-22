import unittest
from unittest.mock import patch
import pg6726_broker_observer_whole as p
import pg6728_original4184_observer_artifacts as q


class ObserverWholeDefinitionTest(unittest.TestCase):
    def test_same_all_inventory_no_oracle_changes(self):
        self.assertIsNotNone(p.declared_inventory())
        self.assertEqual([],q.new_case_identities('HEAD'))

    def test_exact_original_dimensions_no_replay(self):
        raw=q.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6728-original4184-observer-v1')
        self.assertIn("('PG6726', (4184, 643, 1667), 2)",raw)
        self.assertNotIn('mvn ',raw)

    def test_missing_actual127_qualification_blocks_new_whole(self):
        with patch.object(p.subprocess,'check_output',return_value=b''),patch.object(p,'QSHA',None):
            with self.assertRaisesRegex(ValueError,'freeze actual observer127'):
                p.prerequisites('fixture')


if __name__=='__main__':unittest.main()
