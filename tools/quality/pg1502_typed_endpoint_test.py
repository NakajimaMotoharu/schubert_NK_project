import ast
import re
import unittest
from pg1502_retained_pair_owned_handoff_retry import payload

def require(v):
    if not v:raise ValueError('typed endpoint refused')

class TypedEndpointTest(unittest.TestCase):
    def function(self):
        node=next(n for n in ast.parse(payload()).body if isinstance(n,ast.FunctionDef)and n.name=='endpoint')
        ns={'require':require,'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual pure endpoint>','exec'),ns);return ns['endpoint']
    def test_independent_ipv4_and_mapped_word_order(self):
        f=self.function()
        self.assertEqual(('127.0.0.1',5432),f('0100007F:1538'))
        self.assertEqual(('127.0.0.1',5432),f('0000000000000000FFFF00000100007F:1538'))
        self.assertEqual(('127.0.0.1',1),f('0100007F:0001'))
        self.assertEqual(('127.0.0.1',65535),f('0100007F:FFFF'))
        for v in [None,[],0,'','0100007F:0000','0100007F:10000','0100007F:1538\n','0100007F:zzzz','0100007f:1538','0200007F:1538','00000000000000000000000001000000:1538','0000000000000000FFFF00000200007F:1538','7F000001:1538']:
            with self.assertRaises(ValueError):f(v)
    def test_sql_host_not_inet_literal(self):
        raw=payload();self.assertIn("'address',host(client_addr)",raw);self.assertNotIn('client_addr::text',raw)
        self.assertIn("['tcp','tcp6']",raw)

if __name__=='__main__':unittest.main()
