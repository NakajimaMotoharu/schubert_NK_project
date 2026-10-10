"""Fixed actual group1/7scope/full-211 join, no finite-tree expansion."""
import ast
import unittest
from pg1126_current_failed_capture_v4 import payload


class CaptureTest(unittest.TestCase):
    def test_actual_scope_group_source_ancestors_new_slot(self):
        text=payload();ast.parse(text)
        for value in ['failed-capture-v4',"held.project(before['heldWholeMetadata'][1],now,ancestors,'0.1.0-PG1068')",
                      "len(before['heldWholeMetadata'])==7",
                      "ancestor_paths=['/','/opt','/opt/schubert-nk','/opt/schubert-nk/releases']",
                      'artifacts.qualify(', 'backup.qualify(']:
            self.assertTrue(value in text)
        self.assertFalse('failed-capture-v3' in text)
        self.assertFalse("for name,entry in before['trees']['/opt/schubert-nk'].items()" in text)
        self.assertFalse('systemctl start' in text or 'systemctl stop' in text)


if __name__=='__main__':unittest.main()
