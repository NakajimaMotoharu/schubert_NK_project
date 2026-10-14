import ast
import copy
import json
import unittest
from pg2516_current_strict_candidate_sources import TOOLS, ARCHIVE, SOURCE, CURRENT, BEFORE, W
from pg2517_current_strict_candidate_compile import compiler
from pg2518_current_strict_candidate_dispatch import source, STAGE, runtime_namespace
from pg2522_current_strict_candidate_post import payload


class CurrentCandidateConnection(unittest.TestCase):
    def candidate(self):
        return {'actualExit':0, 'candidateSource':SOURCE, 'signatureVerified':True,
                'candidateNotDeployed':True, 'manifestSha256':'a'*64, 'signatureSha256':'b'*64}

    def test_full_compiler_basenames_and_current_owned_abi_are_exact(self):
        raw = compiler()
        for marker in ['pg2517-frozen-v1.safe.json', 'pg2512-candidate-build-v1.safe.json',
                       'pg2514-current-cdbc-before-v2', 'pg2459-frozen-v1.safe.json',
                       'pg2458-question-current-owned-stop-tools-v1', 'pg2428-release-v1',
                       'pg2512-manifest-v1.sig', 'Pg2516NativeArgumentTest']:
            self.assertIn(marker, raw)
        self.assertNotIn('pg2375-frozen', raw)

    def test_dispatch_exact_actual_archive_stage_and_action_names(self):
        raw = source()
        ast.parse(raw)
        for marker in [ARCHIVE, TOOLS + '.tar', 'pg2517-frozen-v1.safe.json', 'pg2518-stage-v1.exit']:
            self.assertIn(marker, raw)
        self.assertIn(TOOLS + '.tar', STAGE)
        self.assertNotIn('pg2433-frozen', raw)

    def test_runtime_joins_real_current_but_rejects_wrong_source_before_and_booleans(self):
        current = json.loads((W / 'pg2514-current-cdbc-before-v2/manifest.safe.json').read_bytes())
        ns = runtime_namespace(self.candidate(), current)
        self.assertEqual(SOURCE, ns['SOURCE'])
        self.assertEqual(BEFORE, ns['BASELINE_SHA'])
        for key, value in [('actualExit',False), ('productionSource','old'), ('privateBeforeSha256','wrong'), ('runtimeAlreadyRetired',False)]:
            wrong = copy.deepcopy(current); wrong[key] = value
            with self.assertRaises(ValueError):
                runtime_namespace(self.candidate(), wrong)
        wrong = self.candidate(); wrong['candidateSource'] = CURRENT
        with self.assertRaises(ValueError):
            runtime_namespace(wrong, current)

    def test_independent_post_reads_actual_current_and_never_repeats_place(self):
        raw = payload(self.candidate())
        ast.parse(raw)
        for marker in ['pg2514-current-cdbc-before-v2', 'pg2520-current-strict-placement-v1',
                       'PG2512', SOURCE, '06236d14-a6f8-4d05-a6ff-49c713cc2647']:
            self.assertIn(marker, raw)
        self.assertNotIn('pg2410-retired-current-before-v1', raw)


if __name__ == '__main__':
    unittest.main()
