"""Pure diagnostic boundaries, separate from actual failing JUnit container proof."""
import ast
import unittest

import pg3370_db_fixture_beforeall_canary as target


class BeforeAllCanaryGates(unittest.TestCase):
    def test_fixed_binding_and_exact_negative_environment_no_maven_replay(self):
        data = {'source': 'literal3706', 'slot': 'independent', 'snapshot': 'unchanged'}
        raw = target.server_source(data)
        binding = next(ast.literal_eval(n.value) for n in ast.parse(raw).body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                       and n.targets[0].id == 'INPUT')
        self.assertEqual(data, binding)
        self.assertIn("env['SCHUBERT_PG_ROOT']='/nonexistent-pgpt-dblife-noexec'", raw)
        self.assertNotIn('mvn', raw)
        self.assertNotIn('skipTests', raw)
        self.assertIn("'newPtCredit':0", raw)

    def test_launcher_requires_original_io_zero_started_and_no_secondary_npe(self):
        raw = (target.ROOT / target.JAVA).read_text()
        for clause in ['getTestsFoundCount() != 1', 'getTestsStartedCount() != 0',
                       'getContainersFailedCount() != 1', '|| !initializationIo', '|| nullPointer',
                       'Files.notExists', 'exp3366001PriorSuccessRevalidatesEveryReadbackWithoutMutation']:
            self.assertIn(clause, raw)
        self.assertNotIn('setAccessible', raw)


if __name__ == '__main__':
    unittest.main()
