"""Actual composed new slot retains current full resources and no business replay authority."""
import unittest
from unittest.mock import patch
import pg2068_retained_backup_replay_history_post as p
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Post(unittest.TestCase):
    def test_full_composition_and_entry(self):
        def entry():
            raw=p.transport.payload({n:'a'*64 for n in SEALS})
            for marker in [p.SLOT,'retained_handle','ALREADY_SUCCESSFUL','same_except_runtime','ordinaryPgRestoreListExit','allClientAdvisoryFlock0']:
                self.assertTrue(marker in raw,marker)
            return 0
        with patch.object(p.transport,'main',entry),patch.object(p.transport,'payload'),patch.object(p.transport,'SLOT','old'):
            self.assertEqual(0,p.main())


if __name__=='__main__':unittest.main()
