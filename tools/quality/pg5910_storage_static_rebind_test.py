import copy
import unittest
from unittest.mock import patch
import pg5910_storage_static_rebind as t


class SourceDiagnosticSequenceTest(unittest.TestCase):
    def rows(self):
        return [dict.fromkeys(t.SEMANTIC, 'same') | {'sourcePath': 'source.java', 'findingId': 'old'+str(i), 'rawXmlOrdinal': 50+i} for i in (1, 2)]

    def test_duplicate_spans_map_bijectively_after_global_ordinal_moves(self):
        old = self.rows(); current = copy.deepcopy(old)
        for i, row in enumerate(current):
            row.update(findingId='new'+str(i), rawXmlOrdinal=20+i)
        pairs = t.ordered_pairs(old, current)
        self.assertEqual([('old1', 1), ('old2', 2)], [(pairs[r['findingId']][0]['findingId'], pairs[r['findingId']][1]) for r in current])
        with patch.object(t.previous, 'bind_one', return_value=({}, 'REBOUND')) as strict:
            value, kind = t.binder(pairs)(current[1], old, b'raw', {'before': 'bytes'}, {'after': 'bytes'})
            self.assertEqual('REBOUND', kind)
            self.assertEqual([old[1]], strict.call_args.args[1])
            self.assertEqual((b'raw', {'before': 'bytes'}, {'after': 'bytes'}), strict.call_args.args[2:])
            self.assertEqual(52, value['priorRawXmlOrdinal'])
            self.assertEqual(2, value['sourceFileOccurrenceRank'])

    def test_every_semantic_change_or_missing_extra_or_nonidentical_swap_is_held(self):
        old = self.rows()
        for key in t.SEMANTIC:
            current = copy.deepcopy(old); current[0][key] = 'changed'
            self.assertFalse(t.ordered_pairs(old, current), key)
        self.assertFalse(t.ordered_pairs(old, old[:1]))
        extra = copy.deepcopy(old) + [dict(old[0], findingId='extra')]
        self.assertFalse(t.ordered_pairs(old, extra))
        distinct = copy.deepcopy(old); distinct[1]['diagnosticTextSha256'] = 'different'
        self.assertFalse(t.ordered_pairs(distinct, list(reversed(distinct))))
        with self.assertRaises(ValueError):
            t.ordered_pairs(old, [old[0], old[0]])

    def test_candidate_mismatch_does_not_bypass_existing_source_owner_checks(self):
        old = self.rows(); pairs = t.ordered_pairs(old, old)
        with patch.object(t.previous, 'bind_one', return_value=({}, 'NO_OR_AMBIGUOUS_PRIOR')) as strict:
            t.binder(pairs)(old[0], [old[1]], b'raw', {}, {})
            self.assertEqual([], strict.call_args.args[1])


if __name__ == '__main__':
    unittest.main()
