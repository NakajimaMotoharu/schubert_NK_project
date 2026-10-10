import unittest
from pg1256_fresh_owned_stop_dispatch_v2 import source

class FreshCorrectedNamespaceTest(unittest.TestCase):
    def test_actual_complete_namespace_and_strict_archive_function(self):
        env={'__name__':'test_generated_dispatch','__file__':__file__}
        exec(compile(source(),'<whole actual new dispatcher>', 'exec'),env)
        self.assertEqual(env['GUEST'],'/var/lib/pgpt-s1-preservation/pg1253-native-tools-v1')
        stage={};exec(env['STAGE'].split('import pathlib,hashlib,json,os,tarfile,stat')[0],stage)
        stage['archive_members']([('a','file')],{'a'})
        for bad in [[('../a','file')],[('a','link')],[('a','file'),('a','file')]]:
            with self.assertRaises(ValueError):stage['archive_members'](bad,{'a'})
        self.assertIn('pg1256-fixed-stage-v1/pg1253-native-tools-v1.tar',env['STAGE'])
        self.assertIn('Pg1253OriginalTupleTest',source())
        self.assertIn('pg1255-fresh-stop-preflight-v2',source())

if __name__=='__main__':unittest.main()
