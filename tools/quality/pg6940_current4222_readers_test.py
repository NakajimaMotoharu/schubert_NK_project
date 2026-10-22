import json
import unittest
from unittest.mock import patch
import pg6934_current4222_sql as sql
import pg6936_current4222_static as static
import pg6938_current4222_jvm as jvm
import pg6944_current4222_trace as trace


class Current4222ReadersTest(unittest.TestCase):
    def test_real_namespaces_and_no_unfrozen_jvm_acceptance(self):
        self.assertIs(sql.read_whole, sql.definition().__globals__['read_whole'])
        self.assertIs(static.read_whole, static.definition().__globals__['read_whole'])
        with patch.object(jvm, 'SQLSHA', None):
            self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        d = trace.definitions('0' * 64, '0' * 64)
        self.assertIs(trace.read_qualified, d['measurement'].__globals__['read_qualified'])
        self.assertEqual(trace.SOURCE, d['measurement'].__globals__['SOURCE'])
        for value in ('PG6930-six-v1', 4222, 660, 1669):
            self.assertIn(value, d['measurement'].__code__.co_consts)

    def test_all_raw_pairs_keep_root_not_reviewed(self):
        old = static.previous.prior.base.load(static.PRIOR, static.PRIOR_SHA, static.OLD)
        raw = json.loads((static.W / 'pg6928-db-fixture-green-original-v1/findings.safe.json').read_bytes())
        self.assertEqual((1409, 1409), (len(raw), len(static.previous.prior.base.ordered_pairs(old, raw))))
        with self.assertRaises(ValueError):
            static.review_changed(raw[0])


if __name__ == '__main__':
    unittest.main()
