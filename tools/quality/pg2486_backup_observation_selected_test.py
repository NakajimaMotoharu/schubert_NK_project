import unittest
from pathlib import Path
from pg2486_backup_observation_selected import FILES, native_input, server


class Selected(unittest.TestCase):
    def test_actual_current_qualifications_and_four_methods(self):
        raw = server()
        for marker in ['source-full-PG2404', 'PG2486-selected-v2', 'PG2474-native-v1',
                       'PG2478-selected-v4', "'tests':'4'", 'len(native_streams)==9',
                       'SCHUBERT_PG_ROOT', 'fixture_xml_sha', 'classByteMismatch']:
            self.assertIn(marker, raw)
        self.assertNotIn('PG2284-native-v1', raw)
        self.assertEqual(9, len(native_input()['files']))
        text = Path(FILES[1]).read_text()
        for prefix in ['mdb2482001', 'mdb2482002', 'mdb2486001', 'mdb2486002']:
            self.assertEqual(1, text.count(prefix))


if __name__ == '__main__':
    unittest.main()
