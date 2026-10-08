"""Fixed source/version/BOM and no executing signing/deployment during contract tests."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


def constant(name):
    tree = ast.parse((ROOT/'pg621_candidate_build.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    return ast.literal_eval(node.value)


class BuilderBinding(unittest.TestCase):
    def test_source_prior_and_version_are_distinct_complete_literals(self):
        self.assertEqual('72fb7440697ee1048a5c0145055dc1cc3c577914', constant('SOURCE'))
        self.assertEqual('23b14a44b10504172e030bbd6625926bf049fb5c', constant('OLD_SOURCE'))
        text = (ROOT/'pg621_candidate_build.py').read_text()
        for expected in ("OLD = W / 'pg600-release-v1'",
                         "FROZEN = W / 'pg620-typed-oracle-six-host-v1'",
                         "NEXT = W / 'pg621-release-v1'",
                         "assert version.read_bytes() == b'0.1.0-PG600\\n'",
                         "version.write_bytes(b'0.1.0-PG621\\n')",
                         "assert gate['knownOracleHold'] is None",
                         'a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'):
            self.assertIn(expected, text)
        self.assertNotIn('0.1.0-PG548', text)
        self.assertIn("verify_delta(old_classes, new_classes) == 1605", text)
        self.assertIn("gate['tests'] == 3467 and gate['suites'] == 512", text)
        compile(text, '<new candidate builder>', 'exec')
        self.assertLess(text.index("verify_delta(old_classes, new_classes)"),
                        text.index('shutil.copytree(OLD, NEXT)'))
        self.assertLess(text.index("assert gate['knownOracleHold']"),
                        text.index("'-sign'"))


if __name__ == '__main__':
    unittest.main()
