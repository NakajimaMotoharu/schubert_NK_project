"""Independent 0x1007 stream vectors for exact class selection."""

import unittest

from jacoco_readonly_exec_subset import decode

SESSION_STREAM = bytes.fromhex('01 c0c0 1007 10 0003 52554e 0000000000000001 0000000000000002')
CLASS_X = bytes.fromhex('11 0000000000000001 0001 58 03 05')
CLASS_XY = bytes.fromhex('11 0000000000000002 0002 5859 09 0101')
CLASS_XYZ = bytes.fromhex('11 0000000000000003 0003 58595a 01 01')
EXPECTED_SESSION = {'labelBytesHex': '52554e', 'startMillis': 1, 'endMillis': 2}


class ClassSelectionScopeTest(unittest.TestCase):
    def test_empty_class_name_is_invalid_even_with_a_known_target(self):
        for invalid in ({''}, {'X', ''}):
            with self.subTest(targets=invalid):
                with self.assertRaisesRegex(ValueError, 'explicit ASCII target names'):
                    decode(SESSION_STREAM + CLASS_X, invalid)

    def test_empty_target_set_accepts_session_structure_without_class_evidence(self):
        self.assertEqual(
            {'classes': {}, 'sessions': [EXPECTED_SESSION], 'totalClassRecords': 0},
            decode(SESSION_STREAM, set()),
        )

    def test_empty_target_set_keeps_only_count_when_class_data_exists(self):
        self.assertEqual(
            {'classes': {}, 'sessions': [EXPECTED_SESSION], 'totalClassRecords': 1},
            decode(SESSION_STREAM + CLASS_X, set()),
        )

    def test_empty_record_name_is_invalid_even_when_not_selected(self):
        empty_class_name = bytes.fromhex('11 0000000000000004 0000 01 01')
        for targets in (set(), {'X'}):
            with self.subTest(targets=targets):
                with self.assertRaisesRegex(ValueError, 'nonempty original class name required'):
                    decode(SESSION_STREAM + CLASS_X + empty_class_name, targets)

    def test_multiple_targets_each_keep_their_own_crc_and_probes(self):
        result = decode(SESSION_STREAM + CLASS_XY + CLASS_XYZ + CLASS_X, {'X', 'XY'})
        self.assertEqual(
            {
                'classes': {
                    'X': {'crc64': '1', 'probeCount': 3, 'hitProbeIds': [0, 2], 'missedProbeIds': [1]},
                    'XY': {
                        'crc64': '2',
                        'probeCount': 9,
                        'hitProbeIds': [0, 8],
                        'missedProbeIds': [1, 2, 3, 4, 5, 6, 7],
                    },
                },
                'sessions': [EXPECTED_SESSION],
                'totalClassRecords': 3,
            },
            result,
        )

    def test_missing_second_target_rejects_partial_match_despite_shared_prefix(self):
        with self.assertRaisesRegex(ValueError, '^one session and all exact target records required$'):
            decode(SESSION_STREAM + CLASS_X + CLASS_XYZ, {'X', 'XY'})
