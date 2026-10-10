import unittest
from pg1258_fresh_ten_native_counter import catalog,code,INSPECTOR,BEFORE,AFTER

class FreshTenNativeScopeTest(unittest.TestCase):
    def test_actual_whole_namespace_and_current_source_only_scope(self):
        hashes={str(i):'a'*64 for i in range(10)}
        s=code(hashes);env={'__name__':'test_generated_native','__file__':__file__,'CAPACITY':{}}
        exec(compile(s,'<actual whole current ten counter>','exec'),env)
        self.assertEqual(env['SOURCE'],'d5b00104280028d9ea81b44c1d1c805f3c2861ed')
        self.assertEqual(env['HASHES'],hashes)
        compile(catalog(),'<actual current catalog>','exec')
        self.assertIn(INSPECTOR+'.terminal.exec',env['PAYLOAD']);self.assertIn(INSPECTOR+'.closing.exec',env['PAYLOAD'])
        self.assertIn('61345315043',env['PAYLOAD']);self.assertIn('61348488918',env['PAYLOAD'])
        self.assertIn(BEFORE,env['PAYLOAD']);self.assertIn(AFTER,env['PAYLOAD'])
        self.assertNotIn('a14cc600a4fd4f2e9d8c4731ad9d754b',s)
        self.assertNotIn('pg1216-native-stop-v1',s)
        for bad in [None,{},dict(hashes,extra='a'*64)]:
            with self.assertRaises(ValueError):code(bad)

if __name__=='__main__':unittest.main()
