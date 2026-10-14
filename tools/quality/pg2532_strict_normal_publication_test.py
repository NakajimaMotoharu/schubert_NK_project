import ast
import unittest
from pg2532_strict_normal_publication_sources import sources, CURRENT_BOM, production, bind, TOOLS
from pg2533_strict_normal_publication_compile import compiler
from pg2534_strict_normal_publication_dispatch import source, stage, REMOTE


class Publication(unittest.TestCase):
    def test_complete_actual_current_candidate_graph_no_double_unit_actions(self):
        values = sources('a'*64); whole = '\n'.join(values.values())
        for name, raw in values.items():
            if name.endswith('.py'):
                ast.parse(raw)
            self.assertNotIn('__STRICT_', raw)
            self.assertNotIn('NORMAL_DAEMON_RELOAD', raw)
        for marker in [CURRENT_BOM, 'a'*64, production(), 'PG2512', 'PG2428',
                       '06236d14-a6f8-4d05-a6ff-49c713cc2647']:
            self.assertIn(marker, whole)
        self.assertIn('pg2528-strict-candidate-host-ro-v1', whole)

    def test_exact_compiler_dispatch_and_stage_basenames(self):
        raw = compiler('a'*64)
        for marker in ['pg2533-frozen-v1.safe.json', 'pg2530-strict-candidate-ro-post-v1',
                       'pg2517-frozen-v1.safe.json', 'pg2516-current-strict-candidate-tools-v1',
                       'pg2512-candidate-build-v1.safe.json']:
            self.assertIn(marker, raw)
        raw = source('a'*64)
        self.assertIn('pg2533-frozen-v1.safe.json', raw)
        self.assertIn('pg2534-stage-v1.exit', raw)
        self.assertIn("'unitExchangeAndReload':False", raw)
        self.assertIn(REMOTE + '/' + TOOLS + '.tar', stage('a'*64))
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2428', stage('a'*64))

    def test_typed_bom_and_overlap_are_strict(self):
        import pg2440_question_normal_publication_sources as old
        for value in [None, '', 'x'*64, 'a'*63]:
            with self.assertRaises(ValueError):
                bind('literal', value)
        self.assertEqual('a'*64 + ' ' + CURRENT_BOM, bind(old.BOM + ' ' + old.CURRENT_BOM, 'a'*64))


if __name__ == '__main__':
    unittest.main()
