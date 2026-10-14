"""Independent literal start/resume and reserved-before-operation checks."""
import ast
import unittest
from pyflakes.api import check
import pg2982_current_resume_observer as observer
import pg2984_current_resume_once as once


class FreshResume(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = observer.namespace()['files']()
        cls.raw = once.payload({n: 'a' * 64 for n in cls.files})

    def test_all_exports_and_only_one_reserved_start(self):
        self.assertEqual({'pg2982_watch_parent.py', 'pg457_stable_actor.py', 'pg462_observer_identity.py'}, set(self.files))
        for name, raw in self.files.items():
            self.assertEqual(0, check(raw, '<complete immutable ' + name + '>'))
        tree = ast.parse(self.raw)
        starts = []
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                values = [getattr(x, 'value', None) for x in node.elts]
                self.assertFalse(any(x in values for x in ['daemon-reload', 'stop', 'restart', 'reset-failed']))
                if 'start' in values:
                    starts.append(values)
        self.assertEqual([['/usr/bin/systemctl', 'start', '--no-block', 'schubert-nk-morning-controller.service']], starts)
        self.assertTrue(self.raw.index("persist('external-start-guard.private.json'") < self.raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        for value in ['originalBudgetSeconds\':1800', 'd10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac', '96757f38127024e527c5356308e1d6337fb1bb50b2e258283bf2d2fc00376423', 'require(len(records)==10)', 'accepted_before=after']:
            self.assertTrue(value in self.raw, value)

    def test_literal_resume_argument_rejects_noargs_foreign_extra(self):
        tree = ast.parse(self.raw)
        expr = next(n.args[0] for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' and 'declaration is not None and' in ast.get_source_segment(self.raw, n))
        code = compile(ast.Expression(expr), '<independent current resume literal>', 'eval')
        main = 'java dev.codex.schubert.nk.batch.file.MorningProcessMain'
        for value, expected in [(None, False), ((0, main, False), False), ((0, main + ' --resume 0dc63b79-3f9a-450c-b2a6-56f86272d272', False), True), ((0, main + ' --resume foreign', False), False), ((0, main + ' --resume 0dc63b79-3f9a-450c-b2a6-56f86272d272 extra', False), False)]:
            self.assertEqual(expected, eval(code, {'declaration': value}))

    def test_already_current_guard_keeps_old_tuple_negative(self):
        for value in ['3b7f3567', 'PG2126', 'current_view']:
            self.assertFalse(value in self.raw, value)
        self.assertTrue('91f5484b-9702-4c7c-97f3-dd5110a853f9' in self.raw)
        self.assertTrue('normalResumePrepared' in observer.source())


if __name__ == '__main__':
    unittest.main()
