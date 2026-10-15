"""Pure whole terminal/rows/seal generation against literal new-activation vectors."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3130_browser_resume_terminal as terminal
import pg3132_browser_resume_rows as rows
import pg3134_browser_resume_full_seal as seal
import pg2994_current_resume_rows as old_rows
import pg3000_current_resume_full_seal as old_seal
import pg3124_browser_resume_live_binding as live


class WholeBrowserRoot(unittest.TestCase):
    def test_browser_guard_keeps_all_four_real_owner_checks(self):
        import pg3140_browser_business_actual as actual
        before = json.loads((W / 'pg3000-current-resume-full-seal-v1/manifest.safe.json').read_bytes())
        done = json.loads((W / 'pg2992-current-resume-terminal-v1/manifest.safe.json').read_bytes())
        raw = actual.guard(before, done, {'activation': '00000000-0000-4000-8000-000000000001'})
        self.assertEqual(0, check(raw, '<complete four-owner Browser guard>'))
        owners = []
        for node in ast.walk(ast.parse(raw)):
            if isinstance(node, ast.List):
                values = [getattr(value, 'value', None) for value in node.elts]
                if 'caddy.service' in values:
                    owners.append(values)
        self.assertEqual(2, len(owners))
        for values in owners:
            self.assertTrue({'artemis.service', 'caddy.service', 'schubert-nk-api.service', 'schubert-nk-web.service'} <= set(values))
        self.assertTrue('00000000-0000-4000-8000-000000000001.done' in raw)
        for bad in [{'actualExit': 143}, {'genuineParentDone': False}, {'productionSource': 'foreign'}]:
            with self.assertRaises(ValueError):
                actual.guard(before, {**done, **bad}, {'activation': 'fixture'})

    def test_new_binding_and_complete_terminal_rows_native16_seal(self):
        old = json.loads((W / 'pg2990-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        binding = {**old['binding'], 'rootPid': old['rootPid'], 'activation': '00000000-0000-4000-8000-000000000001'}
        start = '2026-10-15T02:00:00+00:00'
        all_rows = rows.rebind(old_rows.payload(), binding['activation'], start)
        full = seal.rebind(old_seal.payload(binding), binding, start)
        self.assertEqual(0, check('SOURCE="fixture"\nDIGEST="fixture"\nEXPECTED={}\n' + live.body(), '<whole new binding>'))
        for raw in [all_rows, full]:
            self.assertEqual(0, check(raw, '<whole new current Root acceptance>'))
            compile(raw, '<independent complete payload>', 'exec')
            for old_value in ['pg2984-current-fresh-resume-once-v1', 'd10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac']:
                self.assertFalse(old_value in raw, old_value)
            self.assertTrue('f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24' in raw)
        for literal in ['len(manifest_copy)==16', "'native'", 'ab3fcad3e4f842562c7cd4cd77c5966b81ffba6534cf153c549cc1a5588aa4e2', binding['activation'], 'pg3122-prepared-browser-resume-once-v1', start]:
            self.assertTrue(literal in full, literal)
        for obsolete in ['native_before_anchor', 'pg2964-retained-full-pair-proof-v1', 'len(manifest)==10']:
            self.assertFalse(obsolete in full, obsolete)
        # No lifecycle action is introduced by the acceptance consumers.
        for raw in [all_rows, full, terminal.payload(binding)]:
            for node in ast.walk(ast.parse(raw)):
                if isinstance(node, ast.List):
                    values = [getattr(value, 'value', None) for value in node.elts]
                    self.assertFalse(any(value in values for value in ['start', 'stop', 'restart', 'daemon-reload', 'reset-failed']))

    def test_historical_activations_remain_rejected(self):
        for value in ['74729e17-91c0-43e7-b01f-74f9e6461d6a', '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf']:
            with self.assertRaises(ValueError):
                terminal.payload({'activation': value})


if __name__ == '__main__':
    unittest.main()
