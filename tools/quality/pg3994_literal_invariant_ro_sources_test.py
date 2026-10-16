import ast
import unittest
from bundle_hash_contract import require_bound
from immutable_payload_binding import PROTECTED
import pg3994_literal_invariant_ro_sources as role
import pg3996_literal_invariant_ro_compile as compiler
import pg3998_literal_invariant_ro_dispatch as dispatch
import pg4000_literal_invariant_ro_post as post


def protected(raw):
    return {t.id: ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign)
            for t in n.targets if isinstance(t, ast.Name) and t.id in PROTECTED}


class NewRO(unittest.TestCase):
    def test_all18_actual_source_and_singleton_bundle_preserve_root_oracle(self):
        values = compiler.generated(); self.assertEqual(18, len(values))
        self.assertTrue(require_bound(values['pg3994_native_refs.py'], compiler.sha(compiler.PRIOR / 'bundle.safe.json')))
        normal = role.unused.sources()
        for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
            self.assertEqual(protected(normal['pg3982_' + suffix]), protected(values['pg3994_' + suffix]))
        for bad in [None, '', role.unused.CURRENT_BOM]:
            with self.assertRaises(ValueError): role.sources(bad)

    def test_fixed_old_and_candidate_roles_and_full_ref_closure(self):
        raw = compiler.compiler(); compile(raw, '<new actual RO host ABI>', 'exec')
        for value in ['pg3984-frozen-v1', 'pg3748-release-v1', 'pg3996', 'Pg3982']:
            self.assertIn(value, raw)
        for value in ['pg3768-frozen', 'pg3420-release', 'systemctl', 'daemon-reload']:
            self.assertNotIn(value, raw)
        self.assertIn(role.TOOLS, dispatch.STAGE)
        raw = post.payload(); compile(raw, '<new actual RO independent post>', 'exec')
        for value in ['manager.RefUnit(unit)', 'manager.UnrefUnit(unit)', 'native46Preserved', 'newTenReferencesReturnedNormally', '0.1.0-PG3976', role.SAVE, "'ro'in options", 'candidateHostReadonlyVerified']:
            self.assertIn(value, raw)
        for value in ['start-unit', 'stop-unit', 'daemon-reload', 'poweroff']:
            self.assertNotIn(value, raw)


if __name__ == '__main__': unittest.main()
