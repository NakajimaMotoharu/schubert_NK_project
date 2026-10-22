import unittest
import pg6908_public_delta_scan as p


class PublicDeltaScanTest(unittest.TestCase):
    def test_new_only_output_label_cannot_escape_public_base(self):
        self.assertEqual(p.BASE / 'PG6908-public-delta-scan-v2', p.output('v2'))
        for bad in ('../private', 'v0', 'v1/other', 'V1'):
            with self.assertRaises(ValueError):
                p.output(bad)

    def test_nul_git_paths_preserve_japanese_and_spaces(self):
        names = {'documents/400_PGPT/日本語 文書.md', 'tools/quality/a.py'}
        self.assertEqual(names, p.paths(('\0'.join(sorted(names)) + '\0').encode()))
        self.assertEqual(set(), p.paths(b''))
        for raw in (b'no terminator', b'\0', b'\xff\0'):
            with self.assertRaises((ValueError, UnicodeDecodeError)):
                p.paths(raw)

    def test_known_formats_and_no_raw_value_in_report(self):
        raw = b'first\n' + b'-----BEGIN ' + b'OPENSSH PRIVATE KEY-----\n'
        raw += b'ghp_' + b'A' * 36 + b'\n' + b'AKIA' + b'B' * 16
        result = p.inspect_bytes(raw)
        self.assertEqual({'PRIVATE_KEY_PEM', 'GITHUB_CREDENTIAL', 'AWS_ACCESS_KEY_ID'}, {r['rule'] for r in result})
        self.assertTrue(all(set(r) == {'rule', 'line'} for r in result))
        self.assertEqual([], p.inspect_bytes(b'public synthetic SHA256 abc and ${PASSWORD_PLACEHOLDER}'))


if __name__ == '__main__':
    unittest.main()
