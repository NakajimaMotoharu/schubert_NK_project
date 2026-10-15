import ast
import unittest
import pg3510_signed_current_handoff as h


class HandoffContract(unittest.TestCase):
    def test_complete_emitted_payload_and_core_scope(self):
        raw = h.payload()
        tree = ast.parse(raw)
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertIn('snapshot', functions)
        self.assertIn('ordinary_snapshot', functions)
        core = ast.get_source_segment(raw, functions['ordinary_snapshot'])
        for required in ['units[name]==old', "rows==seal['rows']", "tcp_peers(peers)",
                         "durable==seal['durable']", "native==seal['native']", "runtime==seal['runtime']"]:
            self.assertIn(required, core)
        self.assertNotIn('actors()', core)
        self.assertNotIn('OFD43_128_same', core)
        self.assertEqual(1, raw.count('terminate(410196,8469964,'))
        self.assertNotIn('SIGKILL', raw)
        self.assertLess(raw.index("durable('fresh-complete.private.json'"), raw.index(' terminate(410196'))

    def test_pidfd_identity_durable_reservation_then_one_signal(self):
        calls = []
        value = {'pid': 410196, 'ticks': 8469964}
        def verify(pid, ticks):
            self.assertEqual((410196, 8469964), (pid, ticks))
            calls.append('verify')
            return value
        h.terminate(410196, 8469964, verify, lambda *a: calls.append('durable'),
                    lambda pid: 77, lambda fd: calls.append(('TERM', fd)),
                    lambda fd: True, lambda fd: calls.append(('close', fd)))
        self.assertEqual(['verify', 'verify', 'durable', ('TERM', 77), ('close', 77)], calls)

    def test_changed_identity_and_reservation_failure_issue_no_signal(self):
        for reserve_failure in [False, True]:
            calls = []
            count = [0]
            def verify(pid, ticks):
                count[0] += 1
                return 1 if reserve_failure or count[0] == 1 else 2
            def reserve(*args):
                raise OSError('durability failure')
            with self.subTest(reserve_failure=reserve_failure), self.assertRaises((ValueError, OSError)):
                h.terminate(410196, 8469964, verify, reserve, lambda pid: 77,
                            lambda fd: calls.append('TERM'), lambda fd: True,
                            lambda fd: calls.append('closed'))
            self.assertEqual(['closed'], calls)


if __name__ == '__main__':
    unittest.main()
