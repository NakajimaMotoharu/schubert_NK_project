"""Actual full-source static gate plus independent NUL argv literal."""
import ast
import unittest
from pyflakes.api import check
from pg2019_fresh_resume_live_binding_complete import body


class Binding(unittest.TestCase):
    def test_actual_whole_source_and_argv(self):
        raw=body();self.assertEqual(0,check('SOURCE="fixed"\nDIGEST="fixed"\nEXPECTED={}\n'+raw,'<actual generated whole readonly source>'))
        call=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='endswith')
        self.assertEqual(b'dev.codex.schubert.nk.batch.file.MorningProcessMain\x00--resume\x004148e3e8-f107-431a-ab27-d6e6d1f1772e\x00',eval(compile(ast.Expression(call.args[0]),'<literal actual suffix>','eval')))


if __name__=='__main__':unittest.main()
