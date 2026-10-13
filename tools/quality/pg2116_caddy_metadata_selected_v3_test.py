"""Actual command split oracle; assembly has no PT credit and required tests cannot be skipped."""
import ast
import unittest
from pyflakes.api import check
from pg2116_caddy_metadata_selected_v3 import server

class ScopeContract(unittest.TestCase):
    def test_compile_only_dependencies_and_mandatory_single_test_module(self):
        raw=server()
        self.assertEqual(0,check('HEAD="fixed"\nARCHIVE_SHA="fixed"\n'+raw,'<actual split scope>'))
        tree=ast.parse(raw)
        modules=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='modules'for t in n.targets))
        self.assertEqual(['batch'],ast.literal_eval(modules))
        self.assertNotIn("'-am'",raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)
        self.assertNotIn('-DskipTests',raw)
        self.assertIn("'compile','jar:jar','install:install'",raw)
        self.assertIn("shutil.copytree(b/'m2/repository',repo,symlinks=True)",raw)
        self.assertIn("'dependencyPtCredit':False,'sharedCacheWritten':False",raw)
        self.assertIn("if dependency.returncode==0:r=subprocess.run(args",raw)
        self.assertNotIn('PG2112',raw)

if __name__=='__main__':unittest.main()
