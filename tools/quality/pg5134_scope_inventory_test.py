"""Literal candidate rows, exact source/hash, path/duplicate/foreign rejection; no remote work."""
import unittest
import pg5134_scope_inventory as role


class ScopeInventory(unittest.TestCase):
    def test_actual_fixed_git_query_selects_all_main_files_and_no_test(self):
        rows = role.source_rows().splitlines()
        self.assertEqual(len(rows), 237)
        self.assertEqual(len({row.split(':',3)[1] for row in rows}), 68)
        self.assertTrue(all(row.startswith(role.SOURCE + ':') and '/src/main/java/' in row for row in rows))
        self.assertFalse(any('/src/test/' in row for row in rows))

    def test_exact_source_lines_and_owner_are_candidates_not_success(self):
        path = 'src/schubert-nk-storage/src/main/java/Example.java'
        raw = role.SOURCE + ':' + path + ':2:    ResourceScope.use(\n'
        result = role.inventory(raw, lambda _: b'class Example {\n    ResourceScope.use(\n}\n', {path:'WBS-P003-08'})
        self.assertEqual(result[0]['costOwner'], 'WBS-P003-08')
        self.assertFalse(result[0]['sites'][0]['fixed'])
        self.assertIsNone(result[0]['sites'][0]['retestEvidence'])
        for wrong in (raw + raw, raw.replace(role.SOURCE, 'b' * 40), raw.replace(':2:', ':0:'),
                      raw.replace('/src/main/java/', '/src/test/java/'), raw.replace('/Example.java', '/../Example.java')):
            with self.assertRaises(ValueError): role.inventory(wrong, lambda _: b'', {})
        with self.assertRaises(ValueError): role.inventory(raw, lambda _: b'class Example {\n    different\n}\n', {})


if __name__ == '__main__':
    unittest.main()
