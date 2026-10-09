"""Literal source/current proof/whole21 baseline, no VM or GC normalization."""
import unittest
from pg701_current_baseline import source


class BindingTest(unittest.TestCase):
    def test_current_21_524_idle_and_preserved_old_proofs(self):
        raw=source();compile(raw,'<new current readonly>','exec')
        for text in ('pg701-completed-baseline-v1','pg696-native-stop-v1','pg697-terminal-final-v1.exit',
                     '97ac29b61037e24f78cd730b229a2a720363b3b2b5f51fd39ddc504dfad40516',
                     '6b3dd954959c43c1bbac2164ec9d0c6b','/releases/0.1.0-PG682','==524','len(v)==21',
                     "v['currentBootstrapProofs']",'pg664-bootstrap-existing-v1',"v['runtime']=None",'not list(runtime.iterdir())',
                     'newMetadataScopesNormal','operationAuthority'):
            self.assertIn(text,raw)
        for old in ('pg655-native-stop','pg661-completed','095f6d1d','==514','current_gc_after_known20','systemctl start','daemon-reload'):
            self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
