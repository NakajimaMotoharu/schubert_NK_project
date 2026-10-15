"""Pure complete-consumer checks: no VM, observer, start, or credential access."""
import ast
import unittest
from pyflakes.api import check
import pg3120_prepared_browser_observer as observer
import pg3122_prepared_browser_resume_once as once


class CompletePreparedConsumer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = observer.namespace()['files']()
        cls.raw = once.payload({name: 'a' * 64 for name in cls.files})

    def test_complete_namespace_and_single_durable_start(self):
        self.assertEqual({'pg3120_watch_parent.py', 'pg457_stable_actor.py', 'pg462_observer_identity.py'}, set(self.files))
        for name, raw in self.files.items():
            self.assertEqual(0, check(raw, '<new observer ' + name + '>'))
        self.assertEqual(0, check(self.raw, '<whole current Root-before>'))
        tree = ast.parse(self.raw)
        starts = []
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                values = [getattr(value, 'value', None) for value in node.elts]
                self.assertFalse(any(x in values for x in ['daemon-reload', 'stop', 'restart', 'reset-failed']))
                if 'start' in values:
                    starts.append(values)
        self.assertEqual([['/usr/bin/systemctl', 'start', '--no-block', 'schubert-nk-morning-controller.service']], starts)
        self.assertLess(self.raw.index("persist('external-start-guard.private.json'"), self.raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))

    def test_full_prepared_native_and_retained_parent_contract(self):
        for literal in [
            'pg3104-full-native-resume-preparation-v1', 'pg3100-full-native-resume-tools-v1',
            'zz-pg3100-once-resume.conf', 'f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24',
            'ab3fcad3e4f842562c7cd4cd77c5966b81ffba6534cf153c549cc1a5588aa4e2',
            'require(len(records)==16)', 'native==snapshot()', 'accepted_before=after',
            '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf.done', "'originalBudgetSeconds':1800",
        ]:
            self.assertTrue(literal in self.raw, literal)
        for old in ['pg2984-current-fresh-resume-once-v1', 'pg2982', 'current_view', 'require(len(records)==10)']:
            self.assertFalse(old in self.raw, old)
        # The sealed previous-retirement oracle must still describe its old file;
        # it is not the current prepared runtime and is not rewritten to zz3100.
        old_retirement = [node for node in ast.walk(ast.parse(self.raw)) if isinstance(node, ast.Constant) and isinstance(node.value, str) and 'zz-pg2970' in node.value]
        self.assertEqual(1, len(old_retirement))
        self.assertTrue('def same_except_runtime' in old_retirement[0].value)
        self.assertTrue('pg3106-full-native-resume-independent-post-v1' in observer.source())
        # Sixteen is exact: old ten, missing one, and injected seventeenth fail.
        node = next(n.args[0] for n in ast.walk(ast.parse(self.raw)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' and ast.unparse(n.args[0]) == 'len(records) == 16')
        predicate = compile(ast.Expression(node), '<independent exact native cardinality>', 'eval')
        for count, expected in [(10, False), (15, False), (16, True), (17, False)]:
            self.assertEqual(expected, eval(predicate, {'records': dict.fromkeys(range(count))}))

    def test_literal_resume_does_not_accept_noargs_or_other_run(self):
        node = next(n.args[0] for n in ast.walk(ast.parse(self.raw)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' and 'declaration is not None and' in ast.get_source_segment(self.raw, n))
        predicate = compile(ast.Expression(node), '<independent literal resume>', 'eval')
        main = 'java dev.codex.schubert.nk.batch.file.MorningProcessMain'
        for declaration, expected in [(None, False), ((0, main, False), False), ((0, main + ' --resume foreign', False), False), ((0, main + ' --resume 0dc63b79-3f9a-450c-b2a6-56f86272d272', False), True), ((0, main + ' --resume 0dc63b79-3f9a-450c-b2a6-56f86272d272 extra', False), False)]:
            self.assertEqual(expected, eval(predicate, {'declaration': declaration}))


if __name__ == '__main__':
    unittest.main()
