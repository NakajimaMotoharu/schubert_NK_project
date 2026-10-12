"""Independent one-signal ordering, refusal and actual complete handoff scope."""
import unittest
from pyflakes.api import check
import pg1653_retained_no_db_once_handoff as p


class SingleTermTest(unittest.TestCase):
    def test_reservation_precedes_single_signal_and_close_always(self):
        events = []
        value = {'pid': 289328, 'ticks': 5627480}
        def verify(pid, ticks):
            self.assertEqual((289328, 5627480), (pid, ticks))
            events.append('verify')
            return value
        p.terminate(289328, 5627480, verify, lambda pid, before: events.append('reserve'), lambda pid: events.append('open') or 44, lambda fd: events.append('TERM'), lambda fd: events.append('wait') or True, lambda fd: events.append('close'))
        self.assertEqual(['verify', 'open', 'verify', 'reserve', 'TERM', 'wait', 'close'], events)
        for phase in ['verify2', 'reserve', 'TERM', 'wait']:
            calls = []
            def guard(pid, ticks):
                calls.append('verify')
                return 1 if len(calls) == 1 or phase != 'verify2' else 2
            def work(name):
                calls.append(name)
                if phase == name:
                    raise OSError('independent fault')
                return True
            with self.subTest(phase=phase), self.assertRaises((ValueError, OSError)):
                p.terminate(289328, 5627480, guard, lambda pid, before: work('reserve'), lambda pid: 44, lambda fd: work('TERM'), lambda fd: work('wait'), lambda fd: calls.append('close'))
            self.assertEqual('close', calls[-1])
            if phase in ['verify2', 'reserve']:
                self.assertNotIn('TERM', calls)

    def test_actual_complete_scope_is_static_and_bound(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual SSC272 full handoff>'))
        for literal in ['pid==289328 and ticks==5627480', 'pidfd_send_signal(fd,signal.SIGTERM', 'poll.poll(15000)', 'time.monotonic()+30', 'allOriginalValuesUnchanged', "'oldCloseUnknown':True", 'CURRENT_LOCK_CHECK=free_lock', "len(rows) == 24"]:
            self.assertIn(literal, raw)
        self.assertNotIn('signal.SIGKILL', raw)
        self.assertNotIn('systemctl stop', raw)
        self.assertNotIn('systemctl start', raw)

    def test_published_scope_not_unrelated_old_design_differences(self):
        text = '# example\n\nSSC272：exact authority\n\nolder unrelated text'
        self.assertEqual('SSC272：exact authority', p.design_scope(text, '343_design.md'))
        text = '# ledger\n\n## SSC-272（fixed）\n\nfixed actor\n\nproof\n\n## SSC-271（history）\nold'
        self.assertEqual('## SSC-272（fixed）\n\nfixed actor\n\nproof', p.design_scope(text, 'documents/914_ledger.md'))
        for bad in ['', 'SSC271：old', 'SSC272：one\n\nSSC272：two']:
            with self.assertRaises(ValueError):
                p.design_scope(bad, '343_design.md')


if __name__ == '__main__':
    unittest.main()
