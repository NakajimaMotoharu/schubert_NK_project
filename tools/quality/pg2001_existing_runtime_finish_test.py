"""Actual remaining-only source, fixed inode metadata, no rewrite/unknown producer globals."""
import ast
import unittest
from pyflakes.api import check
from pg2001_existing_runtime_finish_sources import sources
from pg2000_existing_runtime_file import metadata,FILE_META,DIR_META,SHA


class Finish(unittest.TestCase):
    def test_actual_emitted_existing_only_and_all_static(self):
        s=sources();self.assertEqual(20,len(s))
        for name,raw in s.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual '+name+'>'))
        refs=s['pg2001_native_refs.py'];java=s['Pg2001ExistingRuntimeFinish.java']
        self.assertIn('pinned_runtime.reload()',refs);self.assertNotIn('owned_prepare(',refs)
        self.assertNotIn('runtime_tree(',refs);self.assertNotIn('new-runtime.private',refs)
        self.assertIn("k!='configuration'",refs);self.assertIn('pinned_runtime.close();bus.close()',refs)
        self.assertIn('zz-pg1980-once-resume.conf',s['pg2001_resume_contract.py'])
        self.assertIn('pg1995-partial-runtime-recovery-full-post-v1',refs)
        self.assertIn('ONLY_EXISTING_RUNTIME_RELOAD',java)
        tree=ast.parse(s['pg2001_existing_runtime.py'])
        forbidden={'mkdir','chmod','fchmod','unlink','rename','replace','utime'}
        self.assertEqual([],[(n.func.attr,n.lineno)for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in forbidden])
        self.assertTrue('one normal existing-runtime daemon-reload; no retry' in s['pg2001_existing_runtime.py'])

    def test_all_nine_attributes_independent_literal(self):
        class Attributes:
            st_dev=28;st_ino=15250;st_uid=0;st_gid=0;st_mode=33188;st_nlink=1;st_size=644;st_mtime_ns=1791850609774873609;st_ctime_ns=1791850609774873609
        self.assertEqual([28,15250,0,0,33188,1,644,1791850609774873609,1791850609774873609],metadata(Attributes()))
        self.assertEqual([28,15250,0,0,33188,1,644,1791850609774873609,1791850609774873609],FILE_META)
        self.assertEqual([28,5514,0,0,16877,2,60,1791850609774000000,1791850609774000000],DIR_META)
        self.assertEqual('78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec',SHA)


if __name__=='__main__':unittest.main()
