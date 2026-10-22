import json
import unittest
from unittest.mock import patch
import pg6866_current115_web_receivers as sql
import pg6868_current4209_static_join as static
import pg6870_sql58_current_jvm as jvm
import pg6872_current4209_trace as trace


class Current4209ReaderDefinitionTest(unittest.TestCase):
    def test_genuine_begin_identity_and_current_namespace(self):
        begin=json.loads((trace.W/'pg6852-web-deadline-green-v1/begin.safe.json').read_bytes())
        self.assertEqual(begin['source'],trace.SOURCE)
        d=trace.definitions('0'*64,'0'*64)
        self.assertEqual(begin['source'],d['measurement'].__globals__['SOURCE'])
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        self.assertIs(d['publish'].__globals__,d['measurement'].__globals__)
        for v in('PG6862-six-v1',4209,653,1669):self.assertIn(v,d['measurement'].__code__.co_consts)

    def test_definition_only_and_sql_not_unfrozen(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])

    def test_all1409_raw_pairs_and_twenty_two_current_web_spans(self):
        raw=json.loads((static.W/'pg6854-web-deadline-original-v1/findings.safe.json').read_bytes())
        old=static.base.load(static.PRIOR,static.PRIOR_SHA,static.OLD);pairs=static.base.ordered_pairs(old,raw)
        changed=[r for r in raw if r['findingId']not in pairs]
        self.assertEqual((1409,1387,22),(len(raw),len(pairs),len(changed)))
        for row in changed:self.assertTrue(static.review_changed(row)['rawWarningRetained'])
        with self.assertRaises(ValueError):static.review_changed(dict(changed[0],beginline='1'))


if __name__=='__main__':unittest.main()
