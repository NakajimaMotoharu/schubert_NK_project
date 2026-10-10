"""PT-DEP-1054001..004 hand-written Linux ABI and negative vectors."""
import unittest
from pg1054_cold_socket_contract import endpoint,match


class Socket(unittest.TestCase):
    def test_independent_ipv4_ipv6_mapped_and_port_vectors(self):
        for net,raw,expected in (
            ('tcp','0100007F:1538',('127.0.0.1',5432)),
            ('tcp6','00000000000000000000000001000000:1538',('::1',5432)),
            ('tcp6','0000000000000000FFFF00000100007F:1538',('127.0.0.1',5432)),
            ('tcp','00000000:0000',('0.0.0.0',0)),
            ('tcp','FFFFFFFF:FFFF',('255.255.255.255',65535))):
            self.assertEqual(expected,endpoint(net,raw))

    def test_actual_tuple_matches_and_each_identity_component_does_not(self):
        local='0000000000000000FFFF00000100007F:9C40'
        remote='0000000000000000FFFF00000100007F:1538'
        self.assertTrue(match('tcp6',local,remote,'01','127.0.0.1',40000,5432))
        for args in ((local,remote,'02','127.0.0.1',40000,5432),
                     (local,remote,'01','127.0.0.1',40001,5432),
                     (local,remote,'01','127.0.0.1',40000,5433),
                     ('0000000000000000FFFF00000200007F:9C40',remote,'01','127.0.0.1',40000,5432),
                     (local,'0000000000000000FFFF00000200007F:1538','01','127.0.0.1',40000,5432)):
            self.assertFalse(match('tcp6',*args))

    def test_null_unknown_type_length_hex_schema_refused(self):
        for net,value in ((None,'0100007F:1538'),('udp','0100007F:1538'),('tcp',None),('tcp',3),
                          ('tcp','0100007F1538'),('tcp','0100007F:153'),('tcp','0100007Z:1538'),
                          ('tcp','0100007f:1538'),('tcp6','0100007F:1538')):
            with self.assertRaises(ValueError):endpoint(net,value)

    def test_null_remote_host_bool_and_port_boundaries_refused(self):
        for host,port,server,state in ((None,40000,5432,'01'),('10.0.0.1',40000,5432,'01'),
                                       ('127.0.0.1',None,5432,'01'),('127.0.0.1',True,5432,'01'),
                                       ('127.0.0.1',0,5432,'01'),('127.0.0.1',65536,5432,'01'),
                                       ('127.0.0.1',40000,0,'01'),('127.0.0.1',40000,5432,None)):
            with self.assertRaises(ValueError):match('tcp','0100007F:9C40','0100007F:1538',state,host,port,server)


if __name__=='__main__':
    unittest.main()
