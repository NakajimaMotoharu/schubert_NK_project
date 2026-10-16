"""Pure code generation only: fixture done hash does NOT qualify the running parent."""
import ast
import unittest
from pyflakes.api import check
import pg4036_literal_invariant_browser_actual as browser
import pg4038_literal_invariant_browser_composite as composite
import pg4040_literal_invariant_parent_projection as parent
import pg4042_literal_invariant_owned_sources as owned
from pg3870_current_resume_composite_test import constants


class NewBrowserOwnedChain(unittest.TestCase):
    def test_guard_codegen_requires_current_source_done_flag_and_strict_tls(self):
        value = browser.live(); binding = value['binding']
        seal = {'actualExit': 0, 'productionSource': browser.SOURCE, 'observedOwned': {}}
        terminal = {'actualExit': 0, 'productionSource': browser.SOURCE, 'genuineParentDone': True, 'proofHashes': {'done.private': 'a' * 64}}
        raw = browser.guard(seal, terminal, binding); compile(raw, '<fixture guard generation only>', 'exec')
        for marker in [browser.SOURCE, browser.BOM, binding['activation'], 'PG3976', 'independent_tls_peer', 'ssl.CERT_REQUIRED', 'DONE_SHA']: self.assertIn(marker, raw)
        for wrong in [{'actualExit': 1}, {'genuineParentDone': False}, {'productionSource': 'f' * 40}]:
            with self.assertRaises(ValueError): browser.guard(seal, {**terminal, **wrong}, binding)

    def test_frozen_root_oracles_and_historical_data_never_rewritten_by_stop_bind(self):
        value = browser.live(); binding = {**value['binding'], 'rootPid': value['rootPid']}
        original = composite.root.seal_payload(binding)
        chain = {'before': {'history': [{'source': owned.previous.SOURCE}]}, 'after': {'history': []}, 'context': {}}
        raw = composite.compose(original, chain, 'b' * 64); self.assertEqual(0, check(raw, '<new complete immutable composition>'))
        outer = constants(raw); inner = constants(outer['ORACLE'])
        self.assertEqual(chain, inner['CHAIN']); self.assertEqual(constants(original)['GUARD'], outer['GUARD']); self.assertEqual(constants(original)['ORACLE'], inner['ROOT_ORACLE'])
        old_source = owned.previous.SOURCE
        sample = 'SOURCE=' + repr(old_source) + '\nROOT_ORACLE=' + repr('SOURCE=' + repr(old_source)) + '\n'
        rebound = owned.bind(sample); self.assertEqual('SOURCE=' + repr(old_source), constants(rebound)['ROOT_ORACLE'])
        source = next(n.value.value for n in ast.parse(rebound).body if isinstance(n, ast.Assign) and n.targets[0].id == 'SOURCE')
        self.assertEqual(owned.SOURCE, source)
        digest = 'a' + old_source + 'b' * 23; self.assertEqual(digest, owned.role_text(digest))
        projected = parent.payload('a' * 64, browser.BOM); compile(projected, '<new parent18 projection>', 'exec'); self.assertIn(composite.SLOT, projected)
        with self.assertRaises(ValueError): parent.payload('a' * 64, 'f' * 64)


if __name__ == '__main__': unittest.main()
