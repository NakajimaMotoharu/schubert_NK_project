"""Real entry global closure, actual external producer/action/archive/root join."""
import ast
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg1983_fresh_completed_resume_dispatch as entry


class Entry(unittest.TestCase):
    def test_actual_main_has_all_globals_and_closed_action(self):
        raw=entry.source();base=entry.prior.prior.prior
        ns={**base.prior.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE}
        table=symtable.symtable(raw,'<actual entry>','exec').get_children()[0]
        self.assertEqual(set(),{s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()}-set(ns)-set(dir(builtins)))
        exec(compile(raw,'<real entry globals>','exec'),ns)
        with patch.object(base.prior.sys,'argv',['driver','finish-reload']),patch.object(base.prior.subprocess,'check_output')as git:
            with self.assertRaises(ValueError):ns['main']()
            git.assert_not_called()
        self.assertIn('pg1982-frozen-v1.safe.json',raw);self.assertIn('pg1983-qualified-tools-v1.tar',raw)
        self.assertIn("b'PG1980_INPUT_CLOSURE_READY\\n'",raw)
        self.assertEqual('Pg1980FreshResumePreparation',ns['CLASS']);self.assertIn('prepare-resume',raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG1846/operations/batch.jar',raw)
        self.assertIn('pg1983-qualified-tools-v1.tar',entry.STAGE)
        self.assertIn('pg1980-fresh-resume-tools-v1',entry.STAGE)
        self.assertIn('0.1.0-PG1846',entry.STAGE)
        calls=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='ProcessBuilder']
        self.assertEqual([],calls)


if __name__=='__main__':unittest.main()
