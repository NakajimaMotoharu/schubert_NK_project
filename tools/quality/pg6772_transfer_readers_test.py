import json
import unittest
from unittest.mock import patch
import pg6772_current115_transfer_receivers as sql
import pg6774_current4197_transfer_static_join as static
import pg6776_sql58_transfer_jvm as jvm
import pg6778_current4197_transfer_trace as trace


class TransferReaderDefinitionTest(unittest.TestCase):
    def test_only_one_exact_new_calendar_finding_and_all1404_pairs(self):
        raw=json.loads((static.W/'pg6766-transfer-io-original-v2/findings.safe.json').read_bytes())
        old=static.prior.load(static.PRIOR,static.PRIOR_SHA,static.OLD);pairs=static.prior.ordered_pairs(old,raw)
        self.assertEqual((1405,1404),(len(raw),len(pairs)))
        added=[r for r in raw if r['findingId']not in pairs];self.assertEqual(1,len(added))
        self.assertEqual('REQUIRED_CONTRACT',static.review_changed(added[0])['status'])
        with self.assertRaises(ValueError):static.review_changed(dict(added[0],rule='Other'))

    def test_compile_only_and_explicit_new_main1669_measurement_scope(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        d=trace.definitions('0'*64,'0'*64);method=d['measurement']
        self.assertIs(d,method.__globals__);self.assertIs(d,d['publish'].__globals__)
        self.assertIs(trace.read_qualified,method.__globals__['read_qualified'])
        for v in ('PG6768-six-v1',4197,646,1669):self.assertIn(v,method.__code__.co_consts)
        self.assertNotIn(1667,method.__code__.co_consts)


if __name__=='__main__':unittest.main()
