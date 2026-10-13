import unittest
import copy
from pathlib import Path
from pg2490_backup_original_selected import FILES, SOURCE, jdbc_authority, native_input, server


class Selected(unittest.TestCase):
    def test_crc_source_and_typed_success_refuse_unknown_evidence(self):
        hashes = {m: '1' * 64 for m in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']}
        full = {'result': {'jarHashes': hashes}}
        good = {'actualExit': 0, 'source': SOURCE, 'tests': 4, 'FESAbortedNotRun': 0,
                'inputAuthority': {'jarHashes': hashes}, 'execSha256': '2' * 64,
                'coverage': {m: {'classByteMismatch': 0} for m in hashes}}
        self.assertEqual('2' * 64, jdbc_authority(good, full))
        for key, value in [('actualExit', False), ('actualExit', None), ('source', 'foreign'),
                           ('tests', False), ('FESAbortedNotRun', None), ('execSha256', 'unknown')]:
            bad = copy.deepcopy(good); bad[key] = value
            with self.assertRaises(ValueError): jdbc_authority(bad, full)
        for fault in ['missing', 'mismatch', 'false', 'jar']:
            bad = copy.deepcopy(good)
            if fault == 'missing': del bad['coverage']['web']
            elif fault == 'mismatch': bad['coverage']['api']['classByteMismatch'] = 1
            elif fault == 'false': bad['coverage']['batch']['classByteMismatch'] = False
            else: bad['inputAuthority']['jarHashes']['web'] = '3' * 64
            with self.assertRaises(ValueError): jdbc_authority(bad, full)

    def test_current_main_real_db_and_qualified_broker_subset(self):
        raw = server()
        for marker in ['source-full-PG2404', 'PG2490-selected-v2', 'PG2474-native-v1',
                       'PG2478-selected-v4', 'SCHUBERT_PG_ROOT', 'fixture_xml_sha',
                       'extra_library_hashes', 'len(native_streams)==9', 'classByteMismatch', 'PG2486-selected-v2']:
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
