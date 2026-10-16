"""Actual transport command is bounded independently of source-map size."""
import inspect
import unittest
import pg4428_file_whole_qualification as tool


class FileTransport(unittest.TestCase):
    def test_literal_fixed_short_command_never_contains_large_map(self):
        path = '/home/mini/schubert-nk-pgpt/transfer/PG4428-whole-qualified-v1/qualify.private.py'
        self.assertEqual('python3 -B ' + path, tool.command(path))
        self.assertLess(len(tool.command(path).encode()), 256)
        for bad in [path + "'foreign", 'x' * 163840, '', path.replace('4428', '4422')]:
            with self.assertRaises(ValueError): tool.command(bad)
        raw = inspect.getsource(tool.main)
        self.assertIn('copy(payload, destination', raw)
        self.assertIn('value.split()[0] != digest', raw)
        self.assertIn('run(command(path)', raw)
        self.assertNotIn("<<'", raw)


if __name__ == '__main__':
    unittest.main()
