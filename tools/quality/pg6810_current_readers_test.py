import json
import unittest
from unittest.mock import patch
import pg6810_current115_correlation_receivers as sql
import pg6812_current4202_static_join as static
import pg6814_sql58_current_jvm as jvm
import pg6816_current4202_trace as trace


class Current4202ReaderDefinitionTest(unittest.TestCase):
    def test_begin_source_and_real_current_scope_binding(self):
        begin=json.loads((trace.W/'pg6806-web-correlation-positive-v2/begin.safe.json').read_bytes())
        self.assertEqual(begin['source'],trace.SOURCE)
        d=trace.definitions('0'*64,'0'*64)
        self.assertIs(d['measurement'].__globals__,d['publish'].__globals__)
        self.assertEqual(begin['source'],d['measurement'].__globals__['SOURCE'])
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        for value in ('PG6802-six-v1',4202,649,1669):self.assertIn(value,d['measurement'].__code__.co_consts)
        self.assertNotIn('PG6768-six-v1',d['measurement'].__code__.co_consts)

    def test_definitions_do_not_issue_jobs_or_invent_unfrozen_results(self):
        self.assertTrue(callable(sql.definition()))
        with patch.object(static,'QSHA',None):self.assertIsNone(static.definition().__globals__['QSHA'])
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])

    def test_exact_eighteen_current_web_spans_and_preserved_raw(self):
        raw=json.loads((static.W/'pg6800-web-correlation-original-v1/findings.safe.json').read_bytes())
        old=static.prior.base.load(static.PRIOR,static.PRIOR_SHA,static.OLD);pairs=static.prior.base.ordered_pairs(old,raw)
        changed=[r for r in raw if r['findingId']not in pairs]
        self.assertEqual((1405,1387,18),(len(raw),len(pairs),len(changed)))
        for row in changed:self.assertTrue(static.review_changed(row)['rawWarningRetained'])
        with self.assertRaises(ValueError):static.review_changed(dict(changed[0],sourceSha256='0'*64))


if __name__=='__main__':unittest.main()
