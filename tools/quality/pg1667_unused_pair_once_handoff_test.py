"""Independent once-signal ordering and generation-race refusal vectors."""
import unittest
from pyflakes.api import check
from pg782_owned_handoff import terminate
import pg1667_unused_pair_once_handoff as p


class OncePairHandoffTest(unittest.TestCase):
    def test_once_order_and_changed_generation_refusal(self):
        events = []
        def verify(pid, ticks):
            events.append('verify')
            return {'pid': pid, 'ticks': ticks}
        def opened(pid): events.append('open'); return 7
        def reserve(pid, actor): events.append('durable-reserve')
        def send(fd): events.append('term')
        def wait(fd): events.append('finite-wait'); return True
        def close(fd): events.append('close')
        terminate(10, 20, verify, reserve, opened, send, wait, close)
        self.assertEqual(['verify', 'open', 'verify', 'durable-reserve', 'term', 'finite-wait', 'close'], events)
        events.clear()
        def changed(pid, ticks):
            events.append('verify')
            return len(events)
        with self.assertRaises(ValueError): terminate(10, 20, changed, reserve, opened, send, wait, close)
        self.assertEqual(['verify', 'open', 'verify', 'close'], events)

    def test_failed_reservation_never_sends(self):
        events = []
        def reserve(pid, a): raise ValueError('disk failure')
        with self.assertRaises(ValueError):
            terminate(10, 20, lambda pid, ticks: 'fixed', reserve, lambda pid: 7, lambda fd: events.append('term'), lambda fd: True, lambda fd: events.append('close'))
        self.assertEqual(['close'], events)

    def test_actual_generated_complete_binding(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual once current pair handoff>'))
        self.assertLess(raw.index("private('fresh-complete.private'"), raw.index('terminate(291242,5962938'))
        self.assertLess(raw.index('terminate(291242,5962938'), raw.index('terminate(291213,5962776'))
        for text in ['p.poll(15000)', 'time.monotonic()+30', 'parent_after_ref(', 'daemon.NameHasOwner', 'oldCloseUnknown', 'fullIndependentPostPending']:
            self.assertIn(text, raw)
        for text in ['SIGKILL', 'pg_terminate_backend', 'os.kill(']:
            self.assertNotIn(text, raw)


if __name__ == '__main__':
    unittest.main()
