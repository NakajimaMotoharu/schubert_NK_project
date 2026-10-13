import copy
import unittest
from pg2512_strict_reference_signed_candidate import DELTA, PHYSICAL, SOURCE, prior, main_source, validate_gate, verify_delta


class Candidate(unittest.TestCase):
    def test_independent_literal_six_class_delta_rejects_extras_and_omission(self):
        old = {m: {} for m in prior.MODULES}
        for n in range(1640):
            old['batch']['literal-' + str(n)] = 'a' * 64
        for name in DELTA:
            old['batch'][name.split(':', 1)[1]] = 'a' * 64
        new = copy.deepcopy(old)
        for name in DELTA:
            new['batch'][name.split(':', 1)[1]] = 'b' * 64
        self.assertEqual(1643, verify_delta(old, new))
        for mutation in ['missing', 'extra', 'same']:
            value = copy.deepcopy(new)
            if mutation == 'missing':
                value['batch'].pop('literal-0')
            elif mutation == 'extra':
                value['batch']['literal-0'] = 'c' * 64
            else:
                value = copy.deepcopy(old)
            with self.assertRaises(ValueError):
                verify_delta(old, value)

    def test_exact_typed_full_gate_and_negative_missing_boolean_old_source(self):
        gate = {'actualExit':0, 'productionSource':SOURCE, 'tests':3650, 'suites':540,
                'mainClasses':1643, 'FESFlakyNotRun':0, 'staticSixModules':0,
                'classifierFourCounters100':True, 'global100':False, 'formalAccepted':False,
                'semanticChangedClasses':6, 'debugOnlyChangedClasses':1,
                'changedClasses':sorted(PHYSICAL), 'addedClasses':[],
                'debugLineQualification':{'dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class':
                    {'lineEntries':70, 'lineOffset':1, 'nonLineBytesIdentical':True}},
                'jarHashes':{m:'a'*64 for m in prior.MODULES}}
        outer = {'actualExit':0, 'result':gate}
        self.assertIs(gate, validate_gate(outer, SOURCE))
        for key, value in [('tests',3649),('actualExit',False),('productionSource','old'),('staticSixModules',1),('global100',True),('changedClasses',[])]:
            bad = copy.deepcopy(outer);bad['result'][key] = value
            with self.assertRaises(ValueError):
                validate_gate(bad, SOURCE)
        with self.assertRaises(ValueError):
            validate_gate({'actualExit':False, 'result':gate}, SOURCE)

    def test_new_only_signing_namespace_and_no_guest_action(self):
        raw = main_source()
        for marker in ['PG2512', 'PG2428', 'pg2511-strict-reference-full-qualified-v1', SOURCE,
                       "{'VERSION', 'operations/batch.jar'} <= changed"]:
            self.assertIn(marker, raw)
        self.assertNotIn('systemctl', raw)
        self.assertNotIn('ssh', raw)


if __name__ == '__main__':
    unittest.main()
