"""Launcher scope, immutable binding and server-only dependency preconditions."""
import unittest
import pg3920_current_abandoned_boundary as selected


class LauncherDependency(unittest.TestCase):
    def test_missing_coverage_launcher_added_from_independent_success(self):
        source = {'org/jacoco/cli.jar': 'a' * 64}
        historical = {selected.LAUNCHER: selected.LAUNCHER_SHA}
        self.assertEqual({**source, **historical}, selected.runtime_libraries(source, historical))
        self.assertEqual({'org/jacoco/cli.jar': 'a' * 64}, source)

    def test_unknown_version_hash_or_missing_original_binding_refused(self):
        for historical in [{}, {selected.LAUNCHER: '0' * 64}]:
            with self.assertRaises(ValueError):
                selected.runtime_libraries({}, historical)
        for coverage in [{selected.LAUNCHER: '0' * 64}, {selected.LAUNCHER.replace('1.13.4', '1.12.0'): selected.LAUNCHER_SHA}]:
            with self.assertRaises(ValueError):
                selected.runtime_libraries(coverage, {selected.LAUNCHER: selected.LAUNCHER_SHA})

    def test_payload_preserves_main_inputs_and_has_no_historic_union(self):
        raw = selected.server()
        self.assertIn("source-full-PG3734", raw)
        self.assertIn("require(sha(p)==h);libraries.append(str(p))", raw)
        self.assertIn(selected.METHOD, raw)
        self.assertNotIn("['qualificationInputs']", raw)
        self.assertIn("'nativeImported':False", raw)


if __name__ == '__main__':
    unittest.main()
