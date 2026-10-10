"""PT-DEP-1049001..007: independent stateful two-actor sequence/failure oracle."""
import unittest
from pg1049_cold_tree_contract import once_tree


class Tree(unittest.TestCase):
    def run_case(self, fail=None, wait=False, mutate=None):
        calls = []; signals = []; counts = {}
        def act(name, value=None):
            calls.append(name); counts[name] = counts.get(name, 0) + 1
            if name == fail:
                raise RuntimeError('injected')
            if name == mutate and counts[name] > 1:
                return {'generation': 'changed'}
            return value
        def send(fd):
            act('send' + str(fd)); signals.append(fd)
        try:
            once_tree((5463, 1373880), (5489, 1373951),
                      lambda: act('tree', {'generation': 'fixed'}),
                      lambda: act('orphan', {'parentGone': True, 'server0': True, 'child': 'fixed'}),
                      lambda actor, proof: act('reserve' + str(actor[0])),
                      lambda pid: act('open' + str(pid), pid), send,
                      lambda fd: act('wait' + str(fd), not wait),
                      lambda fd: act('close' + str(fd)))
        except BaseException as e:
            return calls, signals, e
        return calls, signals, None

    def test_exact_success_order(self):
        calls, signals, failure = self.run_case()
        self.assertIsNone(failure)
        self.assertEqual([5463, 5489], signals)
        self.assertEqual(['tree','tree','open5463','tree','open5489','tree','reserve5463','tree',
                          'send5463','wait5463','orphan','orphan','reserve5489','orphan',
                          'send5489','wait5489','close5489','close5463'], calls)

    def test_binding_and_parent_reservation_failures_never_signal(self):
        for fault in ('tree', 'open5463', 'open5489', 'reserve5463'):
            calls, signals, failure = self.run_case(fail=fault)
            self.assertIsNotNone(failure); self.assertEqual([], signals)
            if fault in ('open5489', 'reserve5463'):
                self.assertIn('close5463', calls)

    def test_parent_unknown_never_signals_child(self):
        for fault in ('send5463', 'wait5463', 'orphan', 'reserve5489'):
            calls, signals, failure = self.run_case(fail=fault)
            self.assertIsNotNone(failure); self.assertNotIn(5489, signals)
            self.assertEqual(['close5489','close5463'], calls[-2:])

    def test_timeout_never_signals_child_or_retries(self):
        calls, signals, failure = self.run_case(wait=True)
        self.assertIsNotNone(failure); self.assertEqual([5463], signals)
        self.assertEqual(1, calls.count('send5463')); self.assertNotIn('reserve5489', calls)

    def test_changed_tree_or_orphan_is_not_accepted(self):
        for changed in ('tree', 'orphan'):
            calls, signals, failure = self.run_case(mutate=changed)
            self.assertIsNotNone(failure); self.assertNotIn(5489, signals)

    def test_child_send_wait_close_failures_not_success(self):
        for fault in ('send5489', 'wait5489', 'close5489', 'close5463'):
            calls, signals, failure = self.run_case(fail=fault)
            self.assertIsNotNone(failure)
            self.assertLessEqual(calls.count('send5489'), 1)
            self.assertEqual(['close5489','close5463'], calls[-2:])

    def test_null_unknown_equal_pid_and_bad_generation_refused(self):
        for parent, child in ((None,(2,3)),((2,3),None),((2,3),(2,4)),((True,4),(3,5)),((0,4),(3,5)),((2,),(3,5))):
            with self.assertRaises(ValueError):
                once_tree(parent,child,*([None]*7))

    def test_null_callback_is_rejected_before_any_action(self):
        with self.assertRaises(ValueError):
            once_tree((5463,1373880),(5489,1373951),*([None]*7))


if __name__ == '__main__':
    unittest.main()
