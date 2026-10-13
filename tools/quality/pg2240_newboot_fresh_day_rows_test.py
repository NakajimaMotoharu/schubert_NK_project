import ast
import unittest
from pyflakes.api import check
import pg2238_newboot_before_selectors as selectors
import pg2240_newboot_fresh_day_rows as rows


class FreshDayInputs(unittest.TestCase):
    def test_whole_current_before_and_oracle_sha_closure(self):
        binding={'run':'11111111-1111-4111-8111-111111111111','cutoff':'2026-10-13T15:01:00Z'}
        a=selectors.payload(binding,'a'*64);b=rows.payload(binding,'a'*64,'b'*64)
        for raw in [a,b]:
            self.assertEqual(0,check(raw,'<whole readonly graph>'))
            self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',raw)
            self.assertIn('pg2227-newboot-fresh-day-once-v1',raw)
            self.assertIn(binding['cutoff'],raw)
            self.assertNotIn('systemctl start',raw)
        self.assertIn('from cryptography.hazmat.primitives.ciphers.aead import AESGCM',a)
        self.assertIn('pg2238-newboot-before-selectors-v1',b)
        self.assertNotIn("r['business_date']=='2026-10-13'",b)
        self.assertIn('begin isolation level repeatable read read only',b)
        ns={};exec(rows.oracle_source(),ns)
        old=[{'id':1,'value':'kept'},{'id':2,'value':'expired'}]
        self.assertEqual([],ns['delta'](old,[old[0]],'id',['2']))
        for new in [[],[{'id':1,'value':'changed'}],[old[0],old[0]]]:
            with self.assertRaises(ValueError):ns['delta'](old,new,'id',['2'])
        self.assertIsNotNone(ast.parse(a));self.assertIsNotNone(ast.parse(b))


if __name__=='__main__':unittest.main()
