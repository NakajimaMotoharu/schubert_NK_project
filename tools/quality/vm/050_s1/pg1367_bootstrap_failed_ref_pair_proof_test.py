"""Actual failed Ref scope shape and complete protected original join."""
import ast
import unittest
import pg1367_bootstrap_failed_ref_pair_proof as p

class Test(unittest.TestCase):
    def test_actual_pair_bus_and_metadata(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64));ast.parse(raw)
        for value in ('Pg1362BootstrapExisting','pg1362_bootstrap_existing.py','len(names)==1',"'bus':names",'locks[name]=list(metadata9(st))','PG1367-bootstrap-failed-ref-pair-v1'):
            self.assertTrue(value in raw,value)
        self.assertFalse('pidfd_send_signal'in raw)
        self.assertFalse('busNames0'in raw)
        self.assertTrue('native=snapshot();require(native==snapshot()and owner==fixed_owner())'in raw)

if __name__=='__main__':
    unittest.main()
