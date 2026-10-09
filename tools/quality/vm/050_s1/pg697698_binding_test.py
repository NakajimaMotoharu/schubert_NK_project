"""Independent post/counter whole new source bindings, no measurement or authority."""
import unittest
from pg696_binding_test import fixture
from pg697_terminal_final import source
from pg698_native_counter import code,catalog


class BindingTest(unittest.TestCase):
    def test_post_exact_seals_current_signature_all_resources(self):
        raw=source();env={'__file__':__file__,'__name__':'independent_current_binding'}
        exec(compile(raw,'<new readonly post>','exec'),env)
        seals={k:str(i+1)*64 for i,k in enumerate(('before.private.json','after.private.json','parent.private.jsonl','complete.private'))}
        value=env['payload'](fixture(),seals);compile(value,'<new real post>','exec')
        for text in ('pg696-native-stop-v1','pg697-terminal-final-v1','pg682-manifest.sig',
                     'metadata9(p.lstat())==metadata9(s)',"'all24UnchangedTwice':True","'allClientAdvisoryFlock0':True",*seals.values()):
            self.assertIn(text,value)
        for old in ('pg642-native-stop-v1','pg640-completed-readonly-v1','p.lstat()==s','pg631-manifest.sig'):
            self.assertNotIn(old,value)

    def test_new_frozen_host_byte_and_native_window_no_old_source(self):
        hashes={f'fixed{i}.exec':'1'*64 for i in range(8)};seals={'before.private.json':'2'*64,'after.private.json':'3'*64}
        raw=code(hashes,fixture(),seals);compile(raw,'<new native qualification>','exec')
        for text in ('pg696-native-stop-v1','pg697-terminal-final-v1','pg698-current-eight-native-v1',
                     '119288459330','120900000000','6b3dd954959c43c1bbac2164ec9d0c6b',
                     'pg680-owner-six-host-v1','3489','b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6',*seals.values()):
            self.assertIn(text,raw)
        for old in ('pg642-native-stop-v1','pg643-terminal-final-v2','103062293730','104759573609','36fe7a0b','pg630-retention'):
            self.assertNotIn(old,raw)
        value=catalog(seals['before.private.json']);compile(value,'<new readonly catalog>','exec')
        self.assertIn('pg696-native-stop-v1',value);self.assertIn(seals['before.private.json'],value)


if __name__=='__main__':unittest.main()
