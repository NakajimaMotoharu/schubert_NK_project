"""Independent exact multiFD and OFD relation refusal vectors."""
import unittest
from pyflakes.api import check
import pg1651_retained_no_db_readonly_proof_v2 as p


class FdRelationTest(unittest.TestCase):
    def test_attribute_distinct_and_shared_lock_dup(self):
        self.assertEqual(3, len(p.fd_relation('maintenance.lock', ['30', '33', '34'], ['34'], lambda a, b: 1)))
        self.assertEqual([{'a': '43', 'b': '128', 'sameOfd': True}], p.fd_relation('startup-admission.lock', ['43', '128'], ['43', '128'], lambda a, b: 0))
        for name, fds, locks in [('maintenance.lock', ['30', '33', '34'], ['34']), ('startup-admission.lock', ['43', '128'], ['43', '128'])]:
            for result in [-1, None, True, '0', 0 if name == 'maintenance.lock' else 1]:
                with self.assertRaises(ValueError):
                    p.fd_relation(name, fds, locks, lambda a, b: result)
            for bad in [[], fds[:-1], fds + ['999'], None]:
                with self.assertRaises(ValueError):
                    p.fd_relation(name, bad, locks, lambda a, b: 0)
            with self.assertRaises(ValueError):
                p.fd_relation(name, fds, [], lambda a, b: 0)

    def test_complete_generated_readonly_proof_static(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual current multiFD proof>'))
        self.assertIn('libc.syscall(312,289328,289328,0,a,b)', raw)
        self.assertIn('noChild', raw)
        self.assertNotIn('pidfd_send_signal', raw)
        self.assertNotIn('os.kill', raw)


if __name__ == '__main__':
    unittest.main()
