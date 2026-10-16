"""One frozen campaign: honest trigger, digest-safe binding and exact new-case/physical scopes."""
import ast
import unittest
from pyflakes.api import check
import pg3966_literal_invariant_full_six as whole
import pg3968_literal_invariant_whole_qualification as qualify


class CombinedMainCampaign(unittest.TestCase):
    def test_actual_scope_metadata_and_late_bound_source_hashes(self):
        raw = whole.operator_source()
        self.assertIn(whole.BASIS, raw); self.assertIn(whole.TRIGGER, raw); self.assertNotIn('BUG1313', raw)
        head, digest = '0123456789abcdef0123456789abcdef01234567', '3714' + 'a' * 60
        body = whole.server_source(head, digest); literals = [n.value for n in ast.walk(ast.parse(body)) if isinstance(n, ast.Constant)]
        self.assertIn(head, literals); self.assertIn(digest, literals); self.assertIn(whole.SOURCE, literals)
        self.assertNotIn('7fffab57a567914956b66452e5e54388642efdec', literals)
        self.assertIn(3717, literals); self.assertIn('PG3966', body)

    def test_independent_actual_old3716_plus_one_and_only72_source_families(self):
        body = qualify.server_code()
        self.assertEqual(0, check('data={}\nrequire=lambda *a:None\nsource_file=lambda x:None\nclassify=lambda *a:set()\n' + body, '<actual new-Main qualifier namespace>'))
        self.assertIn('len(old_cases) == 3716', body); self.assertIn('len(all_cases) == 3717', body); self.assertIn('len(additions) == 1', body)
        self.assertIn('runs/PG3928-six-v1/manifest.safe.json', body); self.assertIn('source-full-PG3966', body)
        data = qualify.qualification_inputs({'snapshot': 'b' * 40})
        self.assertEqual(72, len(data['approvedChangedSources'])); self.assertEqual(1, len(data['newCases'])); self.assertEqual(1308, data['expected']['batch'][0])


if __name__ == '__main__':
    unittest.main()
