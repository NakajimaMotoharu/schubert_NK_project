import unittest
from pyflakes.api import check
import pg6022_current3973_public as t


class Original3973ProjectionBindingTest(unittest.TestCase):
    def test_complete_namespace_and_exact_current_target_flags(self):
        raw=t.operator_source();names=sorted(k for k in vars(t.engine)if k.isidentifier()and not k.startswith('__')and k!='main')
        self.assertEqual(0,check('='.join(names)+'=None\n'+raw,'<current original6014 projection namespace>'))
        self.assertIn('PG6014-current3973-cases',raw);self.assertIn('changed67ActualFour100',raw)
        self.assertEqual([],t.added_cases())
        data={'source':t.SOURCE,'serverManifestSha256':'0'*64,'archiveSha256':'1'*64,'modules':{}}
        payload=t.payload(data)
        self.assertIn('PG6014',payload);self.assertNotIn('Popen',payload)


if __name__=='__main__':unittest.main()
