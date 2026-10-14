"""Whole final authority graph (not just wrapper) and before residual boot counterexample."""
import unittest
from pyflakes.api import check
import pg2890_network_owned_sources as p


class OwnedGraph(unittest.TestCase):
    def test_final_positive_boot_and_actual_source_every_namespace(self):
        before=p.namespace()['sources']()
        self.assertTrue('epoch.boot().toString().equals("b2d6f605-61cf-425f-8fbd-12d606f6ee66")'in before['Pg2890NativeStop.java'])
        files=p.sources();self.assertEqual(15,len(files))
        self.assertTrue('epoch.boot().toString().equals("79a3260a-e16d-42bf-942a-b914ed144c28")'in files['Pg2890NativeStop.java'])
        self.assertFalse('epoch.boot().toString().equals("b2d6f605' in files['Pg2890NativeStop.java'])
        for name,raw in files.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<whole final '+name+'>'))
            for value in ['pg2704-operation-current-full-seal-v1','pg2706-operation-current-parent-projection-v1','/releases/0.1.0-PG2654']:
                self.assertFalse(value in raw,(name,value))
        self.assertTrue('pg2902-network-after-chr-full-seal-v1'in '\n'.join(files.values()))
        self.assertEqual('39a9f97477f6b7f3ffeff363e716ee520f96b53349906ef6144a224bfd447fe9',p.context()[0])


if __name__=='__main__':unittest.main()
