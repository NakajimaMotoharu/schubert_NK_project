import copy
import unittest
from bundle_hash_contract import require_bound
from pg3994_literal_invariant_ro_sources_test import protected
import pg4002_literal_invariant_publication_sources as role
import pg4004_literal_invariant_publication_compile as compiler
import pg4006_literal_invariant_publication_dispatch as dispatch


class FinitePublication(unittest.TestCase):
    def test_all24_actual_roles_positive_tuple_and_frozen_payload(self):
        values = compiler.generated(); self.assertEqual(24, len(values))
        self.assertTrue(require_bound(values['pg4002_native_refs.py'], compiler.ro_compile.sha(compiler.ro_compile.PRIOR / 'bundle.safe.json')))
        normal = role.ro.sources()
        for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
            self.assertEqual(protected(normal['pg3994_' + suffix]), protected(values['pg4002_' + suffix]))
        current, _, ended = role.ro.unused.current_tuple()
        for name in [role.CLASS + '.java', 'Pg4002TransitionTest.java', 'pg4002_ordinary_publication_contract.py']:
            for value in [current['run'], current['activation'], current['cutoff']]: self.assertIn(value, values[name])
            if name.endswith('.java'): self.assertIn(ended, values[name])

    def test_host_abi_and_dispatch_kind_are_exact_new_finite_not_ro_or_root(self):
        raw = compiler.compiler(); compile(raw, '<full new publication ABI>', 'exec')
        self.assertIn("('transition','TransitionTest')", raw); self.assertIn("'Pg4002'+suffix", raw)
        raw = dispatch.source(); compile(raw, '<new finite publication operator>', 'exec')
        for value in ['pg4004-frozen-v1.safe.json', 'pg4006', 'Pg4002TransitionTest', 'finiteCodeOnlyPublication', 'qualify_fixed(fixed)']:
            self.assertIn(value, raw)
        for value in ['pg3792', 'pg3790-frozen', 'daemon-reload', 'Root/noargs']:
            self.assertNotIn(value, raw)
        required = [role.CLASS + '.class', role.CLASS + '.java', 'Pg4002TransitionTest.class', 'Pg4002TransitionTest.java', 'pg4002_ordinary_publication_contract.py', 'pg4002_native_refs.py']
        fixture = {'actualExit': 0, 'candidateSource': role.SOURCE, 'productionSource': role.CURRENT, 'candidateManifestSha256': role.BOM, 'fileHashes': dict.fromkeys(required, 'a' * 64)}
        dispatch.qualify_fixed(fixture)
        for key, value in [('candidateSource', role.CURRENT), ('actualExit', 1), ('candidateManifestSha256', role.ro.unused.CURRENT_BOM)]:
            wrong = copy.deepcopy(fixture); wrong[key] = value
            with self.assertRaises(ValueError): dispatch.qualify_fixed(wrong)
        wrong = copy.deepcopy(fixture); wrong['fileHashes']['Pg3994CandidateRo.class'] = 'a' * 64
        with self.assertRaises(ValueError): dispatch.qualify_fixed(wrong)


if __name__ == '__main__': unittest.main()
