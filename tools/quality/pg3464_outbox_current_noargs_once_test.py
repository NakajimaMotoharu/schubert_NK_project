import ast
import unittest
from pyflakes.api import check
import pg3462_outbox_current_observer as observer
import pg3464_outbox_current_noargs_once as once


class Current4856Admission(unittest.TestCase):
    def test_observer_exact_new_source_and_same_boot(self):
        raw = observer.source()
        ast.parse(raw)
        for marker in [observer.SOURCE, observer.BOM, 'PG3420', 'pg3462',
                       observer.role.BOOT, once.post.SLOT]:
            self.assertIn(marker, raw)
        self.assertNotIn(observer.old.SOURCE, raw)
        self.assertNotIn('b2d6f605', raw)

    def test_durable_guard_budget_and_actual_preserved_native_only(self):
        raw = once.body()
        ast.parse(raw)
        self.assertEqual(22, once.native_physical_count())
        self.assertIn('require(len(records)==22)', raw)
        self.assertIn(once.SLOT, raw)
        self.assertIn("'replayAllowed':False", raw)
        self.assertIn("'originalBudgetSeconds':1800", raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),
                        raw.index("['/usr/bin/systemctl','start','--no-block'"))
        self.assertIn('native-before-private', raw)

    def test_full_post_projection_has_complete_namespace_and_one_start(self):
        raw = once.payload({'pg3462_watch_parent.py': 'a' * 64})
        self.assertEqual(0, check(raw, '<actual current4856 whole one-use projection>'))
        self.assertEqual(1, raw.count("['/usr/bin/systemctl','start','--no-block'"))
        for marker in ['WATCH_FILES=', 'originalBudgetSeconds', '1800',
                       "require(native==historical_native)",
                       'native-before-manifest.private.json']:
            self.assertTrue(marker in raw, marker)
        self.assertLess(raw.index('require(native==historical_native)'),
                        raw.index("persist('external-start-guard.private.json'"))
        self.assertNotIn('pg2684-operation-current-noargs-once-v2', raw)


if __name__ == '__main__':
    unittest.main()
