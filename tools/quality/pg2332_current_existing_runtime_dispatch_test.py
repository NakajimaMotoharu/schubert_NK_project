import ast
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg2332_current_existing_runtime_finish_dispatch as entry


class FinishEntry(unittest.TestCase):
    def test_actual_current_finish_producer_and_stage_before_ownership(self):
        raw=entry.source();base=entry.previous.previous.previous.template.prior.prior.prior.prior
        ns={**base.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE,'CANDIDATE':entry.SOURCE,'BOM':entry.BOM}
        table=symtable.symtable(raw,'<current existing finish>','exec').get_children()[0]
        needed={s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()}
        self.assertEqual(set(),needed-set(ns)-set(dir(builtins)))
        exec(compile(raw,'<actual existing finish entry>','exec'),ns)
        with patch.object(base.sys,'argv',['driver','prepare-resume']),patch.object(base.subprocess,'check_output')as git:
            with self.assertRaises(ValueError):ns['main']()
            git.assert_not_called()
        guard=ast.parse(raw).body[0].body[0]
        self.assertEqual((['stage'],['finish-runtime']),ast.literal_eval(guard.test.comparators[0]))
        for token in ['pg2331-frozen-v1.safe.json','pg2332-qualified-tools-v1.tar','PG2330_INPUT_CLOSURE_READY','Pg2330ExistingRuntimeFinish','0.1.0-PG2126']:
            self.assertTrue(token in raw,'missing finish boundary '+token)
        for token in ['pg2318','pg2317','Pg2316','PG1846']:
            self.assertFalse(token in raw,'foreign finish authority '+token)
        self.assertIn(entry.REMOTE,entry.STAGE)
        self.assertIn(entry.TOOLS,entry.STAGE)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',entry.STAGE)


if __name__=='__main__':unittest.main()
