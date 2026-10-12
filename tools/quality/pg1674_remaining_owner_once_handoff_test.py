"""Independent gate contention/cleanup/security and complete sole-owner payload."""
from pathlib import Path
import tempfile
import unittest
from pyflakes.api import check
from pg1674_critical_management_gate import management_gate
import pg1674_remaining_owner_once_handoff as p


class CriticalManagementTest(unittest.TestCase):
    def test_same_scope_contention_and_exception_release(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'critical.lock'
            with management_gate(path):
                with self.assertRaises(BlockingIOError):
                    with management_gate(path):self.fail('second guest connection admitted')
            with self.assertRaises(ValueError):
                with management_gate(path):raise ValueError('job refused before signal')
            with management_gate(path):pass
            self.assertEqual(0o600,path.stat().st_mode&0o777)

    def test_foreign_mode_symlink_hardlink_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'critical.lock'
            path.touch(mode=0o644)
            with self.assertRaises(ValueError):
                with management_gate(path):self.fail('public gate accepted')
            path.chmod(0o600)
            link=Path(temp)/'link';link.symlink_to(path)
            with self.assertRaises(OSError):
                with management_gate(link):self.fail('symlink accepted')
            hard=Path(temp)/'hard';hard.hardlink_to(path)
            with self.assertRaises(ValueError):
                with management_gate(path):self.fail('multiple link accepted')

    def test_complete_fixed_source_and_same_connection(self):
        raw=p.payload()
        self.assertEqual(0,check(raw,'<sole owner same connection payload>'))
        for text in ["require(not children)",'fresh_sole_parent(',"a==fresh",'p.poll(15000)','time.monotonic()+30',"before(pid,5962776)==a",'fullIndependentPostPending']:
            self.assertIn(text,raw)
        self.assertEqual(1,raw.count('terminate(291213,5962776,before,'))
        for text in ['terminate(291242', 'pg_terminate_backend', 'signal.SIGKILL','os.kill(']:self.assertNotIn(text,raw)
        self.assertLess(raw.index("private('fresh-complete.private'"),raw.index('terminate(291213,5962776,before,'))


if __name__=='__main__':unittest.main()
