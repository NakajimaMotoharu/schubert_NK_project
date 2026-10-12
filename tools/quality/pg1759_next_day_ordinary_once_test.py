"""Actual source no-double-start, native20-before and same-day guard closure."""
import ast
import unittest
from pg1759_next_day_ordinary_once import payload
from pg1758_next_day_observer import namespace

class Once(unittest.TestCase):
    def test_actual_scope_keeps_one_reserved_start_then_ten_ref_finally(self):
        hashes={n:'1'*64 for n in namespace()['files']()}
        raw=payload(hashes);tree=ast.parse(raw)
        start=raw.index("'/usr/bin/systemctl','start','--no-block'")
        self.assertEqual(1,raw.count("'/usr/bin/systemctl','start','--no-block'"))
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),start)
        self.assertLess(raw.index('require(not today_rows)'),start)
        self.assertLess(raw.index('require(len(records)==20)'),start)
        self.assertIn('originalBudgetSeconds=1800',raw)
        self.assertIn('manager.UnrefUnit(u)',raw)
        self.assertNotIn("save=base/'pg1757-next-business-day-before-v1'",raw)
        self.assertEqual(1,len([n for n in tree.body if isinstance(n,ast.Try)]))

if __name__=='__main__':unittest.main()
