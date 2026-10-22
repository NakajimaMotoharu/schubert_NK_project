import json
import unittest
from unittest.mock import patch
import pg6894_current4213_sql as sql
import pg6896_current4213_static as static
import pg6898_current4213_jvm as jvm
import pg6904_current4213_trace as trace


class Current4213ReadersTest(unittest.TestCase):
    def test_same_source_trace_and_real_globals(self):
        begin = json.loads((trace.W / 'pg6884-data-boundary-selected-v1/begin.safe.json').read_bytes())
        self.assertEqual(begin['source'], trace.SOURCE)
        d = trace.definitions('0' * 64, '0' * 64)
        self.assertEqual(trace.SOURCE, d['measurement'].__globals__['SOURCE'])
        self.assertIs(trace.read_qualified, d['measurement'].__globals__['read_qualified'])
        self.assertIs(d['publish'].__globals__, d['measurement'].__globals__)
        for value in ('PG6890-six-v1', 4213, 656, 1669):
            self.assertIn(value, d['measurement'].__code__.co_consts)

    def test_unfrozen_jvm_and_all1409_raw_pairs(self):
        self.assertTrue(callable(sql.definition()))
        self.assertTrue(callable(static.definition()))
        with patch.object(jvm, 'SQLSHA', None):
            self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        old = static.prior.base.load(static.PRIOR, static.PRIOR_SHA, static.OLD)
        raw = json.loads((static.W / 'pg6886-data-boundary-original-v1/findings.safe.json').read_bytes())
        self.assertEqual((1409, 1409), (len(raw), len(static.prior.base.ordered_pairs(old, raw))))
        with self.assertRaises(ValueError):
            static.review_changed(raw[0])


if __name__ == '__main__':
    unittest.main()
