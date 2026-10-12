"""Actual emitted business-day guard, independent calendar/row counterexamples."""
import ast
import datetime as dt
import unittest
from pg1757_new_day_readonly_before import EXTRA,payload

class Day(unittest.TestCase):
    def test_actual_guard_accepts_only_real_current_day_without_existing_rows(self):
        nodes=ast.parse(EXTRA).body
        first=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='day')
        end=next(i for i,n in enumerate(nodes)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and ast.unparse(n.value)=='require(not today_rows)')
        code=compile(ast.Module(body=nodes[first:end+1],type_ignores=[]),'<actual calendar/row guard>','exec')
        def require(value):
            if not value:raise ValueError('refused')
        class Clock:
            value=dt.datetime(2026,10,13,3,tzinfo=dt.timezone(dt.timedelta(hours=9)))
            @classmethod
            def now(cls,zone):return cls.value.astimezone(zone)
        class Calendar:
            datetime=Clock
            timezone=dt.timezone
            timedelta=dt.timedelta
        def check(rows):exec(code,{'datetime':Calendar,'require':require,'after':{'rows':{'schubert.batch_runs':rows}}})
        check([]);check([{'business_date':'2026-10-12','status':'SUCCESS'}])
        for status in ('RUNNING','FAILED','SKIPPED','SUCCESS'):
            with self.assertRaises(ValueError):check([{'business_date':'2026-10-13','status':status}])
        Clock.value=dt.datetime(2026,10,12,23,59,tzinfo=dt.timezone(dt.timedelta(hours=9)))
        with self.assertRaises(ValueError):check([])
        raw=payload();self.assertEqual(1,raw.count("save=base/'pg1757-next-business-day-before-v1'"));self.assertNotIn("save=base/'pg1731-current-bootstrap-full-post-v1'",raw)

if __name__=='__main__':unittest.main()
