"""Actual STAGE current pin and real entry namespace/byte identity are joined."""
import ast
import builtins
import symtable
import unittest
from pyflakes.api import check
import pg1932_current_partial_reload_dispatch as d
from pg1935_current_partial_reload_full_post import payload


class CurrentStage(unittest.TestCase):
    def test_actual_stage_and_entry_use_same_current_and_immutable_root(self):
        self.assertIn("pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846')",d.STAGE)
        self.assertNotIn('0.1.0-PG1638',d.STAGE)
        self.assertIn(d.REMOTE,d.STAGE);self.assertIn(d.prior.GUEST,d.STAGE)
        self.assertEqual(d.prior.TARGET.name,'pg1925-partial-reload-tools-v1')
        raw=d.source()
        self.assertIn('pg1932-stage-v1.exit',raw);self.assertNotIn('pg1927-',raw)
        self.assertIn('pg1926-frozen-v1.safe.json',raw)
        t=symtable.symtable(raw,'<actual>','exec').get_children()[0]
        needed={s.get_name()for s in t.get_symbols()if s.is_global()and s.is_referenced()}
        ns={**d.prior.prior.__dict__,'sources':d.prior.sources,'TOOLS':d.prior.TOOLS,'CLASS':d.prior.CLASS,'TARGET':d.prior.TARGET,'GUEST':d.prior.GUEST,'REMOTE':d.REMOTE,'STAGE':d.STAGE}
        self.assertEqual(set(),needed-set(ns)-set(dir(builtins)))
        values=[n.value for n in ast.walk(ast.parse(d.STAGE))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
        self.assertEqual(1,values.count('/opt/schubert-nk/releases/0.1.0-PG1846'))
        self.assertEqual(0,check(payload(),'<actual new full post>'))


if __name__=='__main__':unittest.main()
