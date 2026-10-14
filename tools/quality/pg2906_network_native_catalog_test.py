"""Full catalogue uses actual zero-before and current Root budget, old streams excluded."""
import json
import unittest
from pyflakes.api import check
import pg2906_network_current_native_catalog as p


class CurrentNative(unittest.TestCase):
    def test_current_zero_before_and_real10points(self):
        live=json.loads((p.W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
        term=json.loads((p.W/'pg2878-network-newcurrent-terminal-v1/manifest.safe.json').read_bytes())
        receipt=(p.W/p.TOOLS/'pg2890_parent_receipt.py').read_text()
        raw=p.catalog_source(receipt,live['binding'],term['endMonotonicUs'])
        self.assertEqual(0,check('SEALS={}\n'+raw,'<actual whole current native>'))
        for v in ['22cb3a9aa8589859ecdab540cb31ea8e0c06cc07f7ebb7ab171bef4aa3e26b80',p.BOOT,p.SOURCE,
            "'newBootRuntimeExecCount':0","old={}", 'ROOT_END=6027336854','ROOT_START=4396782047','currentBootHadNoHistoricalNative']:
            self.assertTrue(v in raw,v)
        for v in ['b2d6f605','pg2227-newboot-fresh-day-once-v1','pg2684-operation-current-noargs-once-v2','len(old)==28']:
            self.assertFalse(v in raw,v)


if __name__=='__main__':unittest.main()
