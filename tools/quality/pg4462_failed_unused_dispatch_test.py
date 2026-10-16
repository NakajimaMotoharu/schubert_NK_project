"""Closed actual operator, no replay/normal authority or source mismatch."""
import ast
import io
import json
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4462_failed_unused_dispatch as tool


class ExplicitFiniteActions(unittest.TestCase):
    def test_all_frozen_sources_and_three_explicit_actions_are_bound(self):
        raw = tool.source(); compile(raw, '<actual finite operator>', 'exec')
        literals = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        self.assertIn('pg4460-frozen-v1.safe.json', literals)
        self.assertIn('pg4442-failed-current-view-qualified-v1/manifest.safe.json', literals)
        self.assertIn('pg4462-inspect-v1.exit', literals)
        self.assertIn(tool.role.SOURCE, literals)
        self.assertIn(tool.role.ARCHIVE, literals)
        self.assertIn("frozen['completeGraphQualified']is not True", raw)
        self.assertIn("'Pg4444UnusedStage '+action", raw)
        self.assertNotIn('genuineCompletion', raw)
        self.assertIn("['inspect']", raw)
        self.assertEqual(0, check("DIGEST='literal'\nFILES={}\n"+tool.stage_source(), '<actual complete stage>', Reporter(io.StringIO(),io.StringIO())))

    def test_runtime_namespace_keeps_failed_data_and_real_candidate_distinct(self):
        candidate = json.loads((tool.role.W/'pg4432-candidate-build-v1.safe.json').read_bytes())
        namespace = tool.runtime_namespace(candidate)
        self.assertEqual(tool.role.SOURCE, namespace['SOURCE'])
        self.assertEqual(tool.role.BOM, namespace['DIGEST'])
        self.assertEqual(tool.role.BEFORE, namespace['BASELINE_SHA'])
        self.assertEqual(tool.role.REMOTE, namespace['REMOTE'])
        bad = dict(candidate); bad['candidateSource'] = tool.role.CURRENT
        with self.assertRaises(ValueError): tool.runtime_namespace(bad)


if __name__ == '__main__':
    unittest.main()
