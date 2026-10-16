import copy
import hashlib
import inspect
import unittest
import pg4384_half_handoff_recover as subject
import pg4382_half_handoff_stage as stage


class CompleteRemaining(unittest.TestCase):
    def fixture(self):
        base = {'actualExit': 0, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                'BOM': '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
                'boot': '79a3260a-e16d-42bf-942a-b914ed144c28', 'formalAccepted': False}
        return {**base, 'mode': 'recover', 'newTenRefsNormalClose': True, 'signalsIssued': 2,
                'javaSignalsIssued': 0, 'caddyStopsReissued': 0, 'oldScopesNormal': False,
                'partialInspect': {**base, 'mode': 'inspect', 'newScopeNormalClose': True},
                'partialRecover': {**base, 'mode': 'recover', 'newScopeNormalClose': True, 'newStopCount': 5,
                    'caddyPriorStopAuthenticated': True, 'original58917Normal': False, 'recoverySixNormal': True,
                    'canonicalEpochRevoked': True, 'all37StartupEntriesPreserved': True},
                'independentPost': {**{k: v for k, v in base.items() if k != 'boot'}, 'newMARDDBTenRefNormalClose': True, 'independentFailedDoneRecoveryPost': True,
                    'oldParentNormal': False, 'parent143StillFailed': True, 'all24OriginalBackupNativeUnitConfigUnchanged': True,
                    'signalStartStopReloadDbWrites': 0}}

    def test_complete_new_scopes_never_old_normalization(self):
        fixed = self.fixture(); self.assertEqual(fixed, subject.completed(fixed))

    def test_every_field_missing_type_or_foreign_rejected(self):
        fixed = self.fixture()
        for container in [None, 'partialInspect', 'partialRecover', 'independentPost']:
            value = fixed if container is None else fixed[container]
            for key, original in value.items():
                if type(original) is dict: continue
                bad_values = [None, 'foreign', False] if type(original) is not bool else [None, not original, 1]
                for bad in bad_values:
                    changed = copy.deepcopy(fixed); target = changed if container is None else changed[container]; target[key] = bad
                    with self.subTest(container=container, key=key, bad=bad), self.assertRaises(ValueError): subject.completed(changed)
                changed = copy.deepcopy(fixed); target = changed if container is None else changed[container]; del target[key]
                with self.assertRaises(ValueError): subject.completed(changed)
        for key in ['partialInspect', 'partialRecover', 'independentPost']:
            changed = copy.deepcopy(fixed); del changed[key]
            with self.assertRaises(ValueError): subject.completed(changed)

    def test_observer_natural_gate_actual_old_transport_and_no_kill(self):
        raw = inspect.getsource(subject)
        for text in ['acquired.wait(30)', 'fixed_entry.original_receipt', "'retainerSshActualExit': None", 'child.communicate()', 'clean fixed operator', 'exact published remaining-only design']:
            self.assertIn(text, raw)
        self.assertNotIn('child.kill(', raw); self.assertNotIn('child.terminate(', raw)
        hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in stage.files().items()}
        program = subject.bootstrap(hashes)
        self.assertIn('pg4382-half-handoff-tools-v1', program)
        self.assertIn(hashes['keeper.py'], program)


if __name__ == '__main__':
    unittest.main()
