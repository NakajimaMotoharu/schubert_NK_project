import ast
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg2306_current_completed_resume_dispatch as entry


class Entry(unittest.TestCase):
    def test_actual_globals_and_current_stage_action_archive_join(self):
        raw=entry.source()
        base=entry.template.prior.prior.prior.prior
        ns={**base.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE,'CANDIDATE':entry.SOURCE,'BOM':entry.BOM}
        table=symtable.symtable(raw,'<current entry>','exec').get_children()[0]
        globals_used={s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()}
        self.assertEqual(set(),globals_used-set(ns)-set(dir(builtins)))
        exec(compile(raw,'<actual closed entry>','exec'),ns)
        with patch.object(base.sys,'argv',['driver','stop']),patch.object(base.subprocess,'check_output')as git:
            with self.assertRaises(ValueError):ns['main']()
            git.assert_not_called()
        for token in ['pg2305-frozen-v1.safe.json','pg2306-qualified-tools-v1.tar','PG2304_INPUT_CLOSURE_READY','0.1.0-PG2126']:
            self.assertIn(token,raw)
        self.assertNotIn('pg1860-warning-unused-tools',raw)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',entry.STAGE)
        self.assertNotIn('3d69f5af',entry.STAGE)
        self.assertIn(entry.REMOTE,entry.STAGE)
        self.assertIn(entry.TOOLS,entry.STAGE)
        guard=ast.parse(raw).body[0].body[0]
        self.assertEqual((['stage'],['prepare-resume']),ast.literal_eval(guard.test.comparators[0]))


if __name__=='__main__':unittest.main()
