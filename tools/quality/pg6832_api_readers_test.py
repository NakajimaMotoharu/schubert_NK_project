import json
import unittest
from unittest.mock import patch
import pg6832_current115_api_receivers as sql
import pg6834_current4203_static_join as static
import pg6836_sql58_current_jvm as jvm
import pg6838_current4203_trace as trace


class Api4203ReaderDefinitionTest(unittest.TestCase):
    def test_actual_begin_and_future_current_scope(self):
        begin=json.loads((trace.W/'pg6824-api-management-result-selected-v1/begin.safe.json').read_bytes())
        self.assertEqual(begin['source'],trace.SOURCE)
        d=trace.definitions('0'*64,'0'*64)
        self.assertEqual(begin['source'],d['measurement'].__globals__['SOURCE'])
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        self.assertIs(d['publish'].__globals__,d['measurement'].__globals__)
        for v in ('PG6828-six-v1',4203,650,1669):self.assertIn(v,d['measurement'].__code__.co_consts)

    def test_definition_only_without_unfrozen_result(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])

    def test_all_raw_and_eighteen_exact_api_spans(self):
        raw=json.loads((static.W/'pg6826-api-management-result-original-v1/findings.safe.json').read_bytes())
        old=static.base.load(static.PRIOR,static.PRIOR_SHA,static.OLD);pairs=static.base.ordered_pairs(old,raw)
        changed=[r for r in raw if r['findingId']not in pairs]
        self.assertEqual((1405,1387,18),(len(raw),len(pairs),len(changed)))
        for row in changed:self.assertTrue(static.review_changed(row)['rawWarningRetained'])
        with self.assertRaises(ValueError):static.review_changed(dict(changed[0],beginline='1'))


if __name__=='__main__':unittest.main()
