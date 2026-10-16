"""Six new ABI Jars, pinned rules, old diagnostic comparison only."""
import unittest
from pyflakes.api import check, checkPath
import pg4700_ssc299_static as tool


class StaticSSC299(unittest.TestCase):
    def test_six_project_jars_only_rebound_all_external_bytes_preserved(self):
        before = {'/old/schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar': 'a' * 64 for m in tool.old.MODULES}
        before['/external/untouched.jar'] = 'b' * 64
        qualified = {m: str(i) * 64 for i, m in enumerate(tool.old.MODULES)}
        expected = {'/home/mini/schubert-nk-pgpt/source-full-PG4694/src/schubert-nk-' + m + '/target/schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar': qualified[m] for m in tool.old.MODULES}
        expected['/external/untouched.jar'] = 'b' * 64
        self.assertEqual(expected, tool.current_auxiliary(before, qualified))
        with self.assertRaises(ValueError): tool.current_auxiliary(before, {'api': 'a' * 64})
        self.assertEqual('a' * 64, before['/old/schubert-nk-api-0.1.0-SNAPSHOT.jar'])

    def test_actual_standalone_has_all_bindings_and_unrelaxed_rules(self):
        raw = tool.server_source({})
        self.assertEqual(0, check(raw, '<SSC299 diagnostic standalone>'))
        self.assertEqual(0, checkPath(tool.__file__))
        for value in ['source-full-PG4694', 'all849AppliedSourceExact', 'sameCurrentSixJarAbi',
                      'all category rules unchanged', 'original pinned PMD7.28.0', 'F03Accepted=False',
                      'runs/PG4424-shared-manager-static-v1/manifest.safe.json', 'format-order gap remains separate']:
            self.assertIn(value, raw)
        self.assertNotIn('source-full-PG4420', raw)


if __name__ == '__main__': unittest.main()
