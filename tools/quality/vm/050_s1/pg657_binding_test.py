"""Current native streams/start-end/host seals, no actual measurement or VM action."""
import unittest
from pg655_binding_test import fixture
from pg657_native_counter import code,catalog


class Binding(unittest.TestCase):
    def test_new_normal_native_pair_and_current_frozen_host(self):
        hashes={f'fixed{i}.exec':'1'*64 for i in range(8)}
        seals={'before.private.json':'2'*64,'after.private.json':'3'*64}
        raw=code(hashes,fixture(),seals);compile(raw,'<new native qualification>','exec')
        for s in ('pg655-native-stop-v1','pg656-terminal-final-v1','pg657-normal-eight-native-v1','107901545407','109500000000',
                  '095f6d1d7f8442b7b2b44ae59a4314f5','pg630-retention-factory-six-host-v1','3468',*seals.values()):
            self.assertIn(s,raw)
        for s in ('pg642-native-stop-v1','pg643-terminal-final-v2','103062293730','104759573609'):
            self.assertNotIn(s,raw)
        c=catalog(seals['before.private.json']);compile(c,'<new readonly catalog>','exec')
        self.assertIn('pg655-native-stop-v1',c);self.assertIn(seals['before.private.json'],c)


if __name__=='__main__':unittest.main()
