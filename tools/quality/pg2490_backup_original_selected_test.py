import unittest
from pathlib import Path
from pg2490_backup_original_selected import FILES, native_input, server


class Selected(unittest.TestCase):
    def test_current_main_real_db_and_qualified_broker_subset(self):
        raw = server()
        for marker in ['source-full-PG2404', 'PG2490-selected-v1', 'PG2474-native-v1',
                       'PG2478-selected-v4', 'SCHUBERT_PG_ROOT', 'fixture_xml_sha',
                       'extra_library_hashes', 'len(native_streams)==9', 'classByteMismatch']:
            self.assertIn(marker, raw)
        for old in ['PG2284-native-v1', 'source-full-PG2228', 'PG2292-selected-v1']:
            self.assertNotIn(old, raw)
        self.assertEqual(9, len(native_input()['files']))
        self.assertEqual(64, len(native_input()['brokerSelectedExecSha256']))
        launcher = Path(FILES[1]).read_text()
        self.assertIn('mdb2490001SkippedBackupRequiresOriginalManifestAndActualReverseOrderedPair', launcher)
        self.assertIn('mdb2490002TerminalPairRejectsMissingAndExtraDriverRows', launcher)


if __name__ == '__main__':
    unittest.main()
