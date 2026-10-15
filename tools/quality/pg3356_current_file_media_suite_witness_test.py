"""Pure witness gates, not Production PT or coverage credit."""
import ast
import unittest
import xml.etree.ElementTree as ET

import pg3356_current_file_media_suite_witness as target


class WitnessGates(unittest.TestCase):
    def test_all_selected_classes_resolve_without_guessed_files(self):
        for module, names in target.SELECTED.items():
            if names is None:
                continue
            self.assertEqual(len(names), len(set(names)))
            for name in names:
                path = target.ROOT / ('src/schubert-nk-' + module + '/src/test/java/dev/codex/schubert/nk/'
                                      + module + '/' + name.replace('.', '/') + '.java')
                self.assertTrue(path.is_file(), str(path))

    def test_exact_data_binding_and_no_replay_commands(self):
        data = {'source': 'fixed', 'snapshot': 'literal', 'wholeSha256': 'sha', 'testHashes': {}}
        raw = target.server_source(data)
        tree = ast.parse(raw)
        bindings = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'INPUT' for t in n.targets)]
        self.assertEqual([data], bindings)
        self.assertNotIn('subprocess', raw)
        self.assertNotIn('mvn', raw)
        self.assertIn("require(set(source_hashes)==set(INPUT['testHashes'])", raw)
        self.assertIn("'propertiesStdoutArgumentsExported':False", raw)

    def test_real_xml_parser_refuses_failure_skips_and_flaky(self):
        def node(extra=''):
            return ET.fromstring('<testsuite name="Example" tests="1" failures="0" errors="0" skipped="0">'
                                 '<testcase classname="Example" name="literal()">' + extra + '</testcase></testsuite>')
        self.assertEqual(['literal()'], target.project_suite(node(), 'sha')['tests'])
        for child in ['failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure']:
            with self.assertRaises(ValueError):
                target.project_suite(node('<' + child + '/>'), 'sha')


if __name__ == '__main__':
    unittest.main()
