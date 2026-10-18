"""Exact immutable namespace/count bindings and complete projection code; no SSH."""
import inspect
import unittest
from pyflakes.api import check, checkPath
import pg5132_root_whole_public as role


class RootProjection(unittest.TestCase):
    def test_all3814_counts_and_original_artifact_paths(self):
        raw = role.export_source()
        self.assertIn('len(all_cases) != 3814', raw)
        self.assertIn("source = base / 'source-full-PG5128'", raw)
        self.assertIn('transfer/PG5128-source.tar', raw)
        self.assertNotIn('PG4968', raw)
        main = role.main_source()
        self.assertIn("r['tests'] == 3814", main)
        self.assertIn("r['suites'] == 556", main)
        self.assertIn("r['mainClasses'] == 1654", main)
        self.assertIn('pg5130-root-whole-qualified-v1', main)
        self.assertIn('pg5132-root-case-projection-v1', main)
        self.assertNotIn('pg5058-original-case-projection-v2', main)
        self.assertNotIn('mvn', main)

    def test_standalone_export_namespace_and_module_static(self):
        header = ('import hashlib,json,re\nfrom pathlib import Path\nimport xml.etree.ElementTree as ET\n'
                  + inspect.getsource(role.previous.qualify_snapshot) + '\n'
                  + inspect.getsource(role.previous.project_xml) + '\n' + role.export_source()
                  + '\nprint(json.dumps(export({})))\n')
        self.assertEqual(0, check(header, '<actual complete read-only projection>'))
        for path in (role.__file__, __file__): self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
