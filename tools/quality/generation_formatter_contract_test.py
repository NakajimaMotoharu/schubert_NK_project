"""BUG1293: independent canonical literal plus real pinned GJF counterexample."""
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
FORMATTER = Path('/home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar')
FIXTURE = ('final class Probe {\n  final String value =\n'
           '      "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu";\n}\n')


class GenerationFormatContract(unittest.TestCase):
    def test_real_default_rejected_and_exact_canonical_literal_preserved_with_skip(self):
        self.assertEqual('25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4',
                         hashlib.sha256(FORMATTER.read_bytes()).hexdigest())
        java = str(Path(os.environ['JAVA_HOME']) / 'bin/java')
        with tempfile.TemporaryDirectory(prefix='pgpt-format-contract-') as temporary:
            path = Path(temporary) / 'Probe.java'
            path.write_text(FIXTURE)
            default = subprocess.run([java, '-jar', str(FORMATTER), str(path)],
                                     capture_output=True, check=True, text=True, timeout=30).stdout
            corrected = subprocess.run([java, '-jar', str(FORMATTER), '--skip-reflowing-long-strings', str(path)],
                                       capture_output=True, check=True, text=True, timeout=30).stdout
            self.assertNotEqual(FIXTURE, default)
            self.assertEqual(FIXTURE, corrected)
            self.assertEqual(FIXTURE, path.read_text())

    def test_actual_generation_command_carries_both_required_flags_before_files(self):
        tree = ast.parse((ROOT / 'tools/quality/002_verify_generation.py').read_text())
        commands = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'command' for t in n.targets)
                    and isinstance(n.value, ast.List)
                    and any(isinstance(x, ast.Constant) and x.value == '-jar' for x in n.value.elts)]
        self.assertEqual(1, len(commands))
        values = [x.value for x in commands[0].value.elts if isinstance(x, ast.Constant)]
        self.assertEqual(['-jar', '--skip-reflowing-long-strings', '--replace'], values)


if __name__ == '__main__':
    unittest.main()
