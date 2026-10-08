"""Independent post rebinding and metadata9 refusal, no VM actions."""
import unittest
from pg655_binding_test import fixture
from pg656_terminal_final import source


class Binding(unittest.TestCase):
    def test_new_seals_current_proof_and_every_post_guard(self):
        raw=source();env={'__file__':__file__,'__name__':'readonly_binding_test'}
        exec(compile(raw,'<new immutable post>','exec'),env)
        seals={k:str(i+1)*64 for i,k in enumerate(('before.private.json','after.private.json','parent.private.jsonl','complete.private'))}
        p=env['payload'](fixture(),seals);compile(p,'<new genuine post>','exec')
        self.assertIn('pg653-completed-readonly-v1',raw)
        self.assertIn('pg655_parent_receipt.py',raw)
        for text in ('pg655-native-stop-v1','pg656-terminal-final-v1',
                     'metadata9(p.lstat())==metadata9(s)',"'all24UnchangedTwice':True","'allClientAdvisoryFlock0':True"):
            self.assertIn(text,p)
        for text in ('pg642-native-stop-v1','pg640-completed-readonly-v1','p.lstat()==s','.unlink(','daemon-reload'):
            self.assertNotIn(text,p)
        for sha in seals.values():self.assertIn(sha,p)


if __name__=='__main__':unittest.main()
