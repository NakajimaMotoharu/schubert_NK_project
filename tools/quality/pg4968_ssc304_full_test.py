"""Strict full count negatives and actual six-format order / complete server namespace."""
import ast
import inspect
import subprocess
import unittest
from pyflakes.api import check,checkPath
import pg4968_ssc304_full as role


class WholeSource(unittest.TestCase):
    def test_strict_counts_and_actual_format_before_any_pt(self):
        self.assertEqual(role.SOURCE,subprocess.check_output(['git','rev-parse',role.SOURCE],cwd=role.ROOT,text=True).strip())
        raw=role.server_source(role.SOURCE,'b'*64);ns={'__name__':'pure_inspection_no_io'}
        self.assertEqual(0,check(raw,'<complete SSC304 full namespace>'))
        exec(compile(raw,'<pure definitions only>','exec'),ns)
        good=[0,True,[],3791,553,1650]
        self.assertTrue(ns['complete_result'](*good))
        for index,values in {0:[1,143,True,None],1:[False,None],2:[['error'],None],3:[3761,3790,3792],4:[551,552,554],5:[1647,1649,1651]}.items():
            for value in values:
                args=good.copy();args[index]=value;self.assertFalse(ns['complete_result'](*args))
        self.assertLess(raw.index('    format_preflight(args,'),raw.index("with (OUT / 'maven.private.log')"))
        self.assertIn('format-before-pt.safe.json',raw)
        self.assertIn(role.SOURCE,raw);self.assertNotIn(role.previous.SOURCE,raw)
        ast.parse(inspect.getsource(role.main))
        for path in(role.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
