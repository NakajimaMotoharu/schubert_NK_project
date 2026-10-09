"""Independent literal inventory and exhaustive single mutation refusal; no signing."""
import copy
import unittest
from pathlib import Path
from pg682_candidate_contract import verify_delta


class CandidateTest(unittest.TestCase):
    def test_literal_expected_delta_and_all_unknowns(self):
        old = {m: {'literal/Main.class': 'a'*64} for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')}
        # Oracle lists are hand-authored independently from the checked contract's constants.
        changed = {
            'api': ['dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain.class',
                    'dev/codex/schubert/nk/api/maintenance/InspectorLauncher.class',
                    'dev/codex/schubert/nk/api/file/InspectorApplication.class'],
            'bootstrap': ['dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame.class',
                          'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard.class',
                          'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Parent.class']}
        added = {
            'api': ['dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Capture.class',
                    'dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain$Operation.class',
                    'dev/codex/schubert/nk/api/maintenance/InspectorLauncher$Capture.class',
                    'dev/codex/schubert/nk/api/file/InspectorApplication$InspectorProbe.class',
                    'dev/codex/schubert/nk/api/file/InspectorApplication$OwnedOperation.class'],
            'bootstrap': ['dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Clock.class',
                          'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$ParentProbe.class']}
        for module, names in changed.items():
            old[module].update({name: 'b'*64 for name in names})
        new = copy.deepcopy(old)
        for module, names in changed.items():
            new[module].update({name: 'c'*64 for name in names})
        for module, names in added.items():
            new[module].update({name: 'd'*64 for name in names})
        self.assertEqual(19, verify_delta(old, new))
        for module in old:
            for mode in ('added', 'removed', 'changed', 'null', 'bad_digest', 'empty'):
                bad = copy.deepcopy(new)
                if mode == 'added': bad[module]['foreign.class'] = 'd'*64
                if mode == 'removed': del bad[module]['literal/Main.class']
                if mode == 'changed': bad[module]['literal/Main.class'] = 'd'*64
                if mode == 'null': bad[module] = None
                if mode == 'bad_digest': bad[module]['literal/Main.class'] = 'X'*64
                if mode == 'empty': bad[module] = {}
                with self.subTest(module=module, mode=mode), self.assertRaises(ValueError):
                    verify_delta(old, bad)
        for module, names in changed.items():
            for name in names:
                bad = copy.deepcopy(new); bad[module][name] = old[module][name]
                with self.assertRaises(ValueError): verify_delta(old, bad)
        for module, names in added.items():
            for name in names:
                bad = copy.deepcopy(new); del bad[module][name]
                with self.assertRaises(ValueError): verify_delta(old, bad)
        for bad in (None, {}, [], {**new, 'foreign': {}}, old):
            with self.assertRaises(ValueError): verify_delta(old, bad)

    def test_builder_gates_before_copy_or_signature(self):
        text = (Path(__file__).parent/'pg682_candidate_build.py').read_text()
        self.assertIn("gate['tests'] == 3489 and gate['suites'] == 516", text)
        self.assertIn('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6', text)
        self.assertIn("{'VERSION', 'api/api.jar'} <= changed", text)
        self.assertIn('verify_delta(old_classes, new_classes) == 1612', text)
        self.assertLess(text.index('verify_delta(old_classes, new_classes)'), text.index('shutil.copytree(OLD, NEXT)'))
        self.assertLess(text.index("assert gate['knownOracleHold']"), text.index("'-sign'"))
        compile(text, '<newonly candidate>', 'exec')


if __name__ == '__main__':
    unittest.main()
