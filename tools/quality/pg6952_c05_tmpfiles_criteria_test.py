import unittest
import pg6952_c05_tmpfiles_criteria as p


class C05TmpfilesCriteriaTest(unittest.TestCase):
    def fixture(self):
        return '\n'.join((p.ROOT / p.ARTIFACT).read_text().splitlines()) + '\n'

    def test_complete_declaration_without_runtime_access(self):
        self.assertEqual(8, len(p.verify_declaration(self.fixture())))
        self.assertEqual('d! /run/schubert-nk 0755 root root -', p.EXPECTED[0])
        self.assertEqual('f! /run/schubert-nk/startup-admission.lock 0600 root root -', p.EXPECTED[-1])

    def test_no_repair_truncate_cleanup_widen_or_missing_rule(self):
        text = self.fixture()
        for changed in (text.replace('d!', 'd'), text.replace('f!', 'f+!'),
          text.replace('0755', '0700'), text.replace('0600', '0666'),
          text.replace('root root -', 'root root 0'), text.replace('/maintenance.lock', '/*.lock'),
          text.replace('f! /run/schubert-nk/maintenance.lock 0600 root root -', ''), text + 'D! /run 0755 root root -\n'):
            with self.assertRaises(ValueError):
                p.verify_declaration(changed)

    def test_unknown_empty_or_nul_crlf_is_not_accepted(self):
        for text in ('', '# only comment', self.fixture().replace('\n', '\r\n'), self.fixture() + '\0'):
            with self.assertRaises(ValueError):
                p.verify_declaration(text)


if __name__ == '__main__':
    unittest.main()
