"""Actual composed new slot retains current full resources and no business replay authority."""
import unittest
import pg2068_retained_backup_replay_history_post as p
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Post(unittest.TestCase):
    def test_full_composition_and_entry(self):
        old=p.transport.SLOT;old_payload=p.transport.payload
        entry=p.entry();self.assertEqual(p.SLOT,entry.__globals__['SLOT'])
        self.assertIs(p.payload,entry.__globals__['payload'])
        raw=entry.__globals__['payload']({n:'a'*64 for n in SEALS})
        for marker in [p.SLOT,'retained_handle','ALREADY_SUCCESSFUL','same_except_runtime','ordinaryPgRestoreListExit','allClientAdvisoryFlock0']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(old,p.transport.SLOT);self.assertIs(old_payload,p.transport.payload)


if __name__=='__main__':unittest.main()
