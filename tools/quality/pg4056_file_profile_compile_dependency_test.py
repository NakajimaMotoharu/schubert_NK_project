import ast
import tempfile
import unittest
from pathlib import Path
import pg4056_file_profile_compile_dependency as profile


class DependencyTest(unittest.TestCase):
    def test_fixed_bytes_and_missing_or_changed_refused(self):
        original = profile.dependency()
        self.assertGreater(len(original), 1000)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'annotation.jar'
            with self.assertRaises(FileNotFoundError): profile.dependency(p)
            p.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaises(ValueError): profile.dependency(p)
            p.write_bytes(original)
            self.assertEqual(original, profile.dependency(p))

    def test_new_only_and_warning_gate_kept(self):
        raw = profile.payload(); tree = ast.parse(raw)
        self.assertNotIn('pg4054-file-primitive-profile-v1', raw)
        self.assertIn(profile.SLOT, raw)
        self.assertIn("'-Xlint:all', '-Werror'".replace(' ', ''), raw.replace(' ', ''))
        self.assertNotIn('-Xlint:none', raw)
        self.assertNotIn('systemctl stop', raw)
        # Actual target and call structure remain the primitive-only Java main.
        self.assertIn('dev.codex.schubert.nk.batch.file.RootFileReadProfile', raw)
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                             and n.func.id in {'eval', 'exec'} for n in ast.walk(tree)))


if __name__ == '__main__': unittest.main()
