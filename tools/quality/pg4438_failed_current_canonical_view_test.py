"""Full native/data/cursor coverage and still-held phase boundary, no actor operation."""
import ast
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4438_failed_current_canonical_view as subject


class CompleteFailedView(unittest.TestCase):
    def test_original_profile_and_all_original_full_scope_guards_are_retained(self):
        raw = subject.payload(); compile(raw, '<full canonical failed view>', 'exec')
        self.assertEqual(0, check(raw, '<full canonical failed view>', Reporter(io.StringIO(), io.StringIO())))
        self.assertIn('full_first==full_second and journal_first==journal_second', raw)
        self.assertLess(raw.index('full_first,journal_first=canonical_image'), raw.index("child.stdin.write('CONTINUE\\n');child.stdin.flush();remaining=child.communicate"))
        for field in ['units', 'configuration', 'rows', 'pid1', 'startup', 'originals', 'backup', 'extraDurable', 'unitFilesActual', 'runtime', 'native']:
            self.assertIn("'" + field + "'", subject.CANONICAL)
        for guard in ['parent143StillFailed', 'former_issued', 'normal_terminal', 'all24OriginalBackupNativeUnitConfigUnchanged', 'newMARDDBTenRefNormalClose']:
            self.assertIn(guard, raw)
        self.assertEqual(19, len(set(subject.PARENT_FIELDS)))
        self.assertNotIn("['systemctl','start'", raw); self.assertNotIn("['systemctl','stop'", raw)
        tree = ast.parse(subject.CANONICAL)
        image = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'result' for x in n.targets))
        self.assertEqual(11, len(image.value.keys))


if __name__ == '__main__':
    unittest.main()
