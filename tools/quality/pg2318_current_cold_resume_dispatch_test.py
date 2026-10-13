import ast
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg2318_current_cold_resume_dispatch as entry


class ColdEntry(unittest.TestCase):
    def test_actual_producer_globals_source_stage_archive_and_closed_action(self):
        raw=entry.source();base=entry.previous.template.prior.prior.prior.prior
        ns={**base.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE,'CANDIDATE':entry.SOURCE,'BOM':entry.BOM}
        table=symtable.symtable(raw,'<actual cold entry>','exec').get_children()[0]
        needed={s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()}
        self.assertEqual(set(),needed-set(ns)-set(dir(builtins)))
        exec(compile(raw,'<closed current cold dispatch>','exec'),ns)
        with patch.object(base.sys,'argv',['driver','stop']),patch.object(base.subprocess,'check_output')as git:
            with self.assertRaises(ValueError):ns['main']()
            git.assert_not_called()
        for token in ['pg2317-frozen-v1.safe.json','pg2318-qualified-tools-v1.tar','PG2316_INPUT_CLOSURE_READY','0.1.0-PG2126']:
            self.assertTrue(token in raw,'missing current boundary '+token)
        for old in ['pg2304','pg2306','pg2305','pg1980','PG1846']:
            self.assertFalse(old in raw,'historical authority '+old)
        self.assertIn(entry.REMOTE,entry.STAGE)
        self.assertIn(entry.TOOLS,entry.STAGE)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',entry.STAGE)
        guard=ast.parse(raw).body[0].body[0]
        self.assertEqual((['stage'],['prepare-resume']),ast.literal_eval(guard.test.comparators[0]))


if __name__=='__main__':unittest.main()
