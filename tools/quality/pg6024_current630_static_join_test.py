import unittest
from pyflakes.api import check
import pg6024_current630_static_join as t


class Corrected630CurrentWholeJoinTest(unittest.TestCase):
    def test_complete_readonly_namespace_and_no_old_claim_reinstatement(self):
        q,r=t.qualification_source(),t.reader_source();names=sorted(k for k in vars(t.previous.previous.previous)if k.isidentifier()and not k.startswith('__')and k not in('main','qualified_whole'))
        self.assertEqual(0,check('='.join(names)+'=None\n'+q+'\n'+r,'<corrected630 whole join namespace>'))
        self.assertIn('(630, 239, 1348)',r);self.assertIn('PG6014-current3973-cases',q)
        self.assertNotIn('Popen',q+r);self.assertNotIn('subprocess.run',q+r)
        self.assertIn("q['qualificationReceiptSha256'] == sha(rp)",q)
        self.assertIn("q['allPhysicalMainSha256']",q)


if __name__=='__main__':unittest.main()
