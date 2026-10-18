"""New20 post: independent original functions, exact old capsule and actual-terminal guard."""
import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5108_corrected_bootstrap_post as post


class CurrentPost(unittest.TestCase):
    def emit(self, actual=None):
        real=Path.read_bytes
        where=post.role.W/(post.dispatch.SLOT+'-execute-v1.safe.json')
        fixture={'actualExit':0,'productionSource':post.role.SOURCE,'operatorUnchanged':True}
        if actual is not None:fixture.update(actual)
        with patch.object(Path,'read_bytes',lambda p:json.dumps(fixture).encode()if p==where else real(p)):
            return post.payload()

    def test_complete_post_functions_and_normal20_independent_oracles_preserved(self):
        raw=self.emit()
        self.assertEqual(0,check(raw,'<complete current corrected20 independent post>'))
        old=(post.role.W/post.role.before.SLOT/'payload.private.py').read_text()
        functions=lambda text:{n.name:ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)}
        before,after=functions(old),functions(raw)
        for name,body in before.items():self.assertEqual(body,after[name],name)
        for literal in (post.role.BASELINE,post.role.SOURCE,post.role.BOM,post.role.before.SLOT,
                        "CONTRACT['same_terminal_cohort']", "CONTRACT['native_tree']",
                        "boot_before['rows'] == boot_after['rows'] == after['rows']",
                        "'currentCredentialsRetired': True", "'allResources0': True"):
            self.assertTrue(literal in raw,literal)
        self.assertLess(raw.index("terminal = boot_after['units'][bootstrap]"),raw.index('current_bootstrap = show'))
        self.assertLess(raw.index('refs.append(u)'),raw.index('current_bootstrap = show'))

    def test_only_three_recovery_references_bind_to_immutable_preimage(self):
        raw=self.emit()
        for literal in ("retained_native = json.loads(baseline_raw)['native']",
                        "fresh['native'] == retained_native", "post == {'native': retained_native",
                        'hashlib.sha256(baseline_raw).hexdigest() == BASELINE'):
            self.assertTrue(literal in raw,literal)
        self.assertTrue("fresh['native'] == native" not in raw)
        self.assertTrue('hashlib.sha256(snapshot_raw).hexdigest() == BASELINE'not in raw)
        # A missing/moved boundary must refuse, never silently stop checking it.
        with self.assertRaises(ValueError):
            post.bind_recovery_preimage(raw)

    def test_failed_foreign_or_unfixed_execute_never_produces_post_source(self):
        for value in ({'actualExit':1},{'actualExit':False},{'productionSource':'foreign'},{'operatorUnchanged':False}):
            with self.subTest(value=value),self.assertRaises(ValueError):self.emit(value)
        for path in (post.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
