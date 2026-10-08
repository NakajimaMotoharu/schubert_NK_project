"""Readonly full20/new current completion/resources and namespace invariants."""
import unittest
from pg661_current_baseline import source


class Binding(unittest.TestCase):
    def test_current_source_proof_and_full20_readonly(self):
        v=source();compile(v,'<whole20 current baseline>','exec')
        for x in ('pg655-native-stop-v1','c13792efb16007ad6fbdcec310dc9c8a598d9a5bad1b4680bef93384ab092285',
                  '095f6d1d7f8442b7b2b44ae59a4314f5','pg661-completed-baseline-v1','len(v)==20','==514','len(set(paths))==18',"v['namespace']",'before==capture()',"'operationAuthority':False","'runtimeFiles':0"):
            self.assertIn(x,v)
        for x in ('daemon-reload','.unlink(',"['systemctl','start'","['systemctl','stop'",'pg646-completed-baseline-v1'):
            self.assertNotIn(x,v)


if __name__=='__main__':unittest.main()
