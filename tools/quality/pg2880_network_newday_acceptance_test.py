"""Fixed new terminal/independent before/day15 all24 graph checks; no runtime action."""
import unittest
from pyflakes.api import check
import pg2878_network_newcurrent_terminal as terminal
import pg2880_network_newday_rows as rows


class CurrentAcceptance(unittest.TestCase):
    def test_same_current_terminal_and_previous_data_rejected(self):
        b={'boot':'79a3260ae16d42bf942ab914ed144c28','invocation':'d4197711cfc54770a4ac7c8d90a3a576','job':'11471','start':4396782047,
            'run':'0dc63b79-3f9a-450c-b2a6-56f86272d272','cutoff':'2026-10-14T19:12:28.842213Z','activation':'74729e17-91c0-43e7-b01f-74f9e6461d6a','rootPid':27414}
        raw=terminal.payload(b);self.assertEqual(0,check(raw,'<complete current terminal>'))
        for v in [terminal.SOURCE,terminal.BOM,'PG2802',b['run'],b['activation']]:self.assertTrue(v in raw,v)
        for value in [dict(b,run='77601cf8-0ade-40fd-813f-c81d5210845e'),dict(b,activation='26250063-8755-43b6-9ac7-f76d5eee7257')]:
            with self.assertRaises(ValueError):terminal.payload(value)

    def test_independent_day15_original_counts_not_observed_results(self):
        raw=rows.payload();self.assertEqual(0,check(raw,'<full day15 namespace>'))
        for v in ["r['business_date']=='2026-10-15'",'pg2876-network-admission-original-v2/oracle.private.json',
            'pg2872-network-newcurrent-noargs-once-v2/external-before.private.json', "before={'rows':captured['immutable']['rows']}",
            "r['attempt']==1",'len(before)==24','expectedSessionDeleted','expectedInboxProtected']:
            self.assertTrue(v in raw,v)
        self.assertFalse("r['business_date']=='2026-10-13'"in raw)
        self.assertFalse('pg1759-next-day-ordinary-once-v1'in raw)


if __name__=='__main__':unittest.main()
