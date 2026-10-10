import ast
import unittest
from pg1132_current_failed_capture_v6 import payload


class CaptureTest(unittest.TestCase):
    def test_all_three_raw_reads_preserved_full_values_compared_no_operations(self):
        raw = payload(); tree = ast.parse(raw)
        self.assertIsInstance(tree, ast.Module)
        for part in ['failed-capture-v6', 'JOURNAL_READS.append(journals)',
                     'journals-before.private.json', 'journals-after.private.json',
                     'journal.project(bytes.fromhex(value))', 'value=capture();require(value==capture())',
                     'require(value==capture())', 'manager.UnrefUnit(u)', 'bus.close()']:
            self.assertIn(part, raw)
        for part in ['systemctl start', 'systemctl stop', 'failed-capture-v5']:
            self.assertNotIn(part, raw)


if __name__ == '__main__': unittest.main()
