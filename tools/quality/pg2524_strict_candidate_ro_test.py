import ast
import unittest
from pg2524_strict_candidate_ro_sources import sources, TOOLS
from pg2525_strict_candidate_ro_compile import compiler
from pg2526_strict_candidate_ro_dispatch import source, STAGE
from pg2530_strict_candidate_ro_post import payload
from pg2516_current_strict_candidate_sources import SOURCE


class NewReadOnly(unittest.TestCase):
    def test_complete_current_candidate_graph_and_actual_basename(self):
        values = sources('a'*64)
        for name, body in values.items():
            if name.endswith('.py'):
                ast.parse(body)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2512', values['pg2524_input_preflight.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2428', values['Pg2524CandidateRo.java'])
        self.assertIn('06236d14-a6f8-4d05-a6ff-49c713cc2647', values['pg2524_parent_receipt.py'])
        tree = ast.parse(values['pg2524_native_refs.py'])
        constants = {n.targets[0].id:ast.literal_eval(n.value) for n in tree.body
                     if isinstance(n, ast.Assign) and len(n.targets) == 1
                     and isinstance(n.targets[0], ast.Name) and n.targets[0].id in {'START', 'END'}}
        self.assertEqual({'START':29104365495, 'END':30827355356}, constants)
        for invalid in [None, 'x'*64, 'a'*63]:
            with self.assertRaises(ValueError):
                sources(invalid)

    def test_compiler_and_dispatch_have_one_exact_ro_role(self):
        raw = compiler()
        for marker in ['pg2525-frozen-v1.safe.json', 'pg2522-current-strict-candidate-post-v1',
                       'pg2517-frozen-v1.safe.json', 'pg2512-candidate-build-v1.safe.json']:
            self.assertIn(marker, raw)
        raw = source()
        self.assertIn('pg2525-frozen-v1.safe.json', raw)
        self.assertIn('pg2526-stage-v1.exit', raw)
        self.assertIn(TOOLS + '.tar', STAGE)

    def test_independent_post_requires_current_reader_and_exact_host_mount(self):
        raw = payload({'actualExit':0, 'candidateSource':SOURCE, 'signatureVerified':True,
                       'manifestSha256':'a'*64, 'signatureSha256':'b'*64})
        self.assertIn('pg2528-strict-candidate-host-ro-v1', raw)
        self.assertIn('pg2514-current-cdbc-before-v2', raw)
        self.assertIn("'--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2512'", raw)
        self.assertIn("'ro'in mounts and 'rw'not in mounts", raw)


if __name__ == '__main__':
    unittest.main()
