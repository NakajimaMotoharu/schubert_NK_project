"""Actual child scope + fullsource/zeroDB/protected values remain explicit."""
import ast
import unittest
import pg1360_bootstrap_failed_pair_proof as p

class Test(unittest.TestCase):
    def test_whole_actual_pair_payload(self):
        raw = p.payload(dict.fromkeys(p.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64))
        ast.parse(raw)
        for value in ('len(kids)==1', "'child':child", 'pg1356_bootstrap_existing.py',
                      'busNames0', 'PG1360-bootstrap-failed-pair-v1',
                      "locks[name]=list(metadata9(st))", "lines[-2:]==[b'0',b'0']"):
            self.assertTrue(value in raw, value)
        self.assertFalse('pidfd_send_signal' in raw)
        self.assertFalse('Pg1348BootstrapExisting' in raw)

if __name__ == '__main__':
    unittest.main()
