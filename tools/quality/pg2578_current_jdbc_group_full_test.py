import ast
import subprocess
import unittest
from pyflakes.api import check
import pg2578_current_jdbc_group_full_six as full
import pg2579_current_jdbc_group_full_qualified as qualified
import pg2582_current_jdbc_group_native_qualified as native


class GroupedFull(unittest.TestCase):
    def test_latest_exact_selected_test_file_and_actual_independent_a01(self):
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        full.validate(head)
        with self.assertRaises(ValueError):
            full.validate(full.SOURCE)

    def test_fresh_full3653_namespace_and_independent_all_xml_static_main_count(self):
        raw = full.server_source('a'*40, 'b'*64)
        self.assertEqual(0, check(raw, '<fresh full compile fixture>'))
        ast.parse(raw)
        for marker in ['PG2578', '3653', '540', '1643']:
            self.assertIn(marker, raw)
        for marker in ['PG2578', '3653', "'batch':(1256,172,568)", 'semanticChangedClasses',
                       'RootStartupContext$NativeIo.class', 'BrokerJournalEvidence.class']:
            self.assertIn(marker, qualified.server())

    def test_current_ten_points_latest_nine_no_replay_and_fresh_whole_source(self):
        raw = native.server()
        ast.parse(raw)
        for marker in ['PG2582-native-v1', 'source-full-PG2578', 'runs/PG2578-six-v1',
                       '3653', 'len(streams)==9', 'inspectorLatestClosingOnly', full.SOURCE]:
            self.assertIn(marker, raw)
        self.assertIn('pg2562-strict-current-native-catalog-v1', native.source())
        self.assertIn('pg2579-current-jdbc-group-full-qualified-v1', native.source())


if __name__ == '__main__':
    unittest.main()
