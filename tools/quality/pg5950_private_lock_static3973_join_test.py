import unittest
from pyflakes.api import check
import pg5950_private_lock_static3973_join as t


class Current573JoinDefinitionTest(unittest.TestCase):
    def test_complete_generated_namespace_is_read_only_and_true_result_bound(self):
        q, r = t.qualification_source(), t.reader_source()
        names = sorted(k for k in vars(t.previous.previous) if k.isidentifier() and not k.startswith('__') and k not in ('main', 'qualified_whole'))
        raw = '='.join(names)+'=None\n'+q+'\n'+r
        self.assertEqual(0, check(raw, '<pure current573 join definitions>'))
        self.assertIn('PG5944-current3973-cases', q); self.assertIn('(573, 239, 1451)', r)
        self.assertNotIn('Popen', raw); self.assertNotIn('subprocess.run', raw)
        self.assertIn("q['qualificationReceiptSha256'] == sha(rp)", q)
        self.assertIn("q['allPhysicalMainSha256']", q)


if __name__ == '__main__':
    unittest.main()
