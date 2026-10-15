import unittest

from pg3328_stream_ownership_audit import inspect_text


class OwnershipAuditTest(unittest.TestCase):
    def test_original_direct_terminal_rejected(self):
        value = inspect_text('assertEquals(6, Files.list(temporary).count());')
        self.assertEqual('MANUAL_REVIEW_REQUIRED', value[0]['ownership'])

    def test_lexical_resources_for_all_operations(self):
        for operation in ['list', 'walk', 'find', 'lines']:
            for prefix in ['', 'java.nio.file.']:
                value = inspect_text('try (var entries = ' + prefix + 'Files.' + operation + '(root)) {')
                self.assertEqual('LEXICAL_TRY_RESOURCE', value[0]['ownership'])

    def test_assignment_and_other_same_line_call_not_admitted(self):
        self.assertEqual('MANUAL_REVIEW_REQUIRED', inspect_text('var value = Files.walk(root);')[0]['ownership'])
        value = inspect_text('try (var value = Files.list(root)) { Files.lines(other).count(); }')
        self.assertEqual(['LEXICAL_TRY_RESOURCE', 'MANUAL_REVIEW_REQUIRED'], [x['ownership'] for x in value])
        self.assertEqual([], inspect_text('ordinaryReference();'))


if __name__ == '__main__':
    unittest.main()
