import json
import unittest
from unittest.mock import patch
import pg6752_current115_owned_receivers as sql
import pg6754_current4189_owned_static_join as static
import pg6756_sql58_owned_jvm as jvm
import pg6758_current4189_owned_trace as trace


class OwnedReaderDefinitionTest(unittest.TestCase):
    def test_no_changed_main_diagnostics_allowed_and_all1404_exact_pairs(self):
        raw=json.loads((static.W/'pg6746-request-read-original-v1/findings.safe.json').read_bytes())
        old=static.prior.load(static.PRIOR,static.PRIOR_SHA,static.OLD)
        self.assertEqual((1404,1404),(len(raw),len(static.prior.ordered_pairs(old,raw))))
        with self.assertRaises(ValueError):static.review_changed({})

    def test_compile_readers_without_running_or_inventing_current_results(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        d=trace.definitions('0'*64,'0'*64)
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        self.assertIn('PG6748-six-v1',d['measurement'].__code__.co_consts)
        self.assertIn(4189,d['measurement'].__code__.co_consts)


if __name__=='__main__':unittest.main()
