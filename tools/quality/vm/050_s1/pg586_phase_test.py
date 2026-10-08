"""Independent bash OR-list first-error gate regression; no files or external actions."""
import pathlib
import subprocess
import unittest


class Test(unittest.TestCase):
    def test_both_phase_gating_and_literal_exit(self):
        for first, second, output, code in ((1, 0, '', 1), (0, 0, 'SELECTED\n', 0), (0, 2, 'SELECTED\n', 2)):
            result = subprocess.run(['bash', '-c', f'set -e; status=0; ((exit {first}) && (printf "SELECTED\\n"; exit {second})) || status=$?; exit "$status"'], capture_output=True, text=True)
            self.assertEqual(output, result.stdout)
            self.assertEqual(code, result.returncode)
            self.assertEqual('', result.stderr)
        source = pathlib.Path(__file__).with_name('pg586_access_selected_v1.sh').read_text()
        self.assertIn('install -DskipTests &&\n./mvnw', source)


if __name__ == '__main__':
    unittest.main()
