import ast
import unittest
import pg6090_original3985_artifacts as p


class OriginalArtifactDefinitionTest(unittest.TestCase):
    def test_exact_old_fixture_suffixes_and_six_new_semantic_case_identities(self):
        rows = p.new_case_identities()
        self.assertEqual(6, len(rows))
        self.assertEqual(6, len(p.reader.expected_case_keys(rows)))
        self.assertEqual({'api', 'web'}, {r['module'] for r in rows})

    def test_complete_readonly_emitted_reader_has_explicit_campaign(self):
        raw = p.reader.emitted('0'*64, '/home/mini/schubert-nk-pgpt/transfer/PG6090-original3985-v1')
        ast.parse(raw)
        self.assertIn("('PG6088', (3985, 595, 1667), 5)", raw)
        self.assertIn("campaign != 'PG6088'", raw)
        self.assertIn("coverage_artifacts[module]", raw)
        for value in ('mvn ', 'systemctl', 'qemu-system', 'sudo ', '--resume', '--recover'):
            self.assertNotIn(value, raw)


if __name__ == '__main__':
    unittest.main()
