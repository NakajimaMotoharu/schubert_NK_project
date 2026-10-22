import json
import unittest
from unittest.mock import patch
import pg6730_current115_observer_receivers as sql
import pg6732_current4184_observer_static_join as static
import pg6734_sql58_observer_jvm as jvm
import pg6736_current4184_observer_trace as trace


class ObserverReaderDefinitionTest(unittest.TestCase):
    def test_current_all22_changed_diagnostics_exact_and_no_blanket_context(self):
        raw=json.loads((static.W/'pg6724-broker-observer-qualification-v1/findings.safe.json').read_bytes())
        old=static.prior.load(static.PRIOR,static.PRIOR_SHA,static.OLD)
        pairs=static.prior.ordered_pairs(old,raw)
        self.assertEqual((1404,1382),(len(raw),len(pairs)))
        changed=[r for r in raw if r['findingId'] not in pairs]
        self.assertEqual(22,len(changed))
        for row in changed:
            self.assertEqual(row['sourceSha256'],static.sha(static.ROOT/row['sourcePath']))
            self.assertTrue(static.review_changed(row)['rawWarningRetained'])
        with self.assertRaises(ValueError):static.review_changed(dict(sourcePath='Other.java'))

    def test_readers_compile_without_running_checks_or_whole(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        d=trace.definitions('0'*64,'0'*64)
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        self.assertIn('PG6726-six-v1',d['measurement'].__code__.co_consts)


if __name__=='__main__':unittest.main()
