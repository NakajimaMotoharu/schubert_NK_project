"""Independent argv byte and selected/new activation condition vectors."""
import ast
import unittest
from pg2017_fresh_resume_live_binding import body


class Binding(unittest.TestCase):
    def test_actual_selected_argv_and_new_activation(self):
        raw=body();tree=ast.parse(raw)
        call=next(n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='endswith')
        wanted=b'dev.codex.schubert.nk.batch.file.MorningProcessMain\x00--resume\x004148e3e8-f107-431a-ab27-d6e6d1f1772e\x00'
        self.assertEqual(wanted,eval(compile(ast.Expression(call.args[0]),'<actual argv suffix>','eval')))
        self.assertTrue("fields[3]!='9adbf05a-61d0-408b-b51d-ab19c7e5b16a'"in raw)
        self.assertTrue("fields[2]=='2026-10-12T18:20:32.598894Z'"in raw)


if __name__=='__main__':unittest.main()
