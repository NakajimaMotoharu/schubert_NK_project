"""Exact case-count bindings, empty physical-change permission, namespace and digest integrity."""
import ast
import unittest
from pyflakes.api import check
import pg3928_current_boundary_full_six as whole
import pg3930_current_boundary_whole_qualification as qualify


class FixedIntegration(unittest.TestCase):
    def test_operator_describes_actual_test_group_not_old_hygiene(self):
        raw = whole.operator_source()
        self.assertIn(whole.BASIS, raw)
        self.assertIn(whole.TRIGGER, raw)
        self.assertNotIn('BUG1313', raw)
        self.assertNotIn('Root inode value/ACL boundary cases', raw)

    def test_whole_keeps_real_hashes_and_exact_expected_count(self):
        head = '0123456789abcdef0123456789abcdef01234567'
        digest = '3714' + 'a' * 60
        raw = whole.server_source(head, digest)
        literals = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        self.assertIn(head, literals)
        self.assertIn(digest, literals)
        self.assertIn(3716, literals)
        self.assertNotIn(3714, [v for v in literals if type(v) is int])
        self.assertIn('PG3928', raw)

    def test_independent_originals_current_inputs_and_no_main_delta_allowed(self):
        raw = qualify.server_code()
        self.assertEqual(0, check('data={}\nrequire=lambda *a:None\nsource_file=lambda x:None\nclassify=lambda *a:set()\n' + raw, '<standalone qualification>'))
        self.assertIn('source-full-PG3928', raw)
        self.assertIn('runs/PG3734-six-v1/manifest.safe.json', raw)
        self.assertIn('len(old_cases) == 3714', raw)
        self.assertIn('len(all_cases) == 3716', raw)
        data = qualify.qualification_inputs({'snapshot': 'b' * 40})
        self.assertEqual([], data['approvedChangedSources'])
        self.assertEqual(1307, data['expected']['batch'][0])
        self.assertEqual(2, len(data['newCases']))


if __name__ == '__main__':
    unittest.main()
