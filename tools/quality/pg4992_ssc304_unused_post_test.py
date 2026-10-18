"""Independent structural/negative oracle checks; no VM or Production PT credit."""
import ast
from collections import Counter
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
from immutable_payload_binding import PROTECTED
import pg4992_ssc304_unused_post as post


def capsules(raw):
    return Counter(ast.get_source_segment(raw, n) for n in ast.walk(ast.parse(raw))
                   if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                   and t.id in PROTECTED for t in n.targets))


class IndependentPost(unittest.TestCase):
    def test_complete_current_and_distinct_candidate_under_refs(self):
        raw = post.payload()
        self.assertEqual(0, check(raw, '<independent current04bb/all80>'))
        self.assertEqual(capsules(post.current.payload()), capsules(raw))
        tree = ast.parse(raw)
        outer = next(n for n in tree.body if isinstance(n, ast.Try)
                     and 'manager.UnrefUnit(u)' in ast.unparse(n.finalbody))
        held = ast.unparse(outer.body)
        for marker in ["0.1.0-PG4980", "0.1.0-PG4860", "pg4980-manifest.sig",
                       post.current.SLOT + '/before.private.json',
                       "sum((p.endswith('.exec') for p in native)) == 80",
                       'json.loads(before) == expected', "'native80Preserved': True",
                       "'guestFilesWritten': 3"]:
            self.assertIn(marker, held)
        final = tree.body[-1]
        self.assertGreater(final.lineno, outer.end_lineno)
        self.assertIn('**candidate_post', ast.unparse(final))
        self.assertIn("'newTenReferencesReturnedNormally': len(refs) == 10", ast.unparse(final))
        assigns = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                   and n.targets[0].id in ('CANDIDATE', 'CURRENT_VIEW_CANDIDATE_SOURCE')}
        self.assertEqual(post.role.SOURCE, assigns['CURRENT_VIEW_CANDIDATE_SOURCE'])
        self.assertEqual(post.role.SOURCE, assigns['CANDIDATE']['candidateSource'])
        self.assertEqual(1, raw.count('def complete_configuration('))
        for name in (post.__file__, __file__):
            self.assertEqual(0, checkPath(name))

    def test_identifier_rename_preserves_literals_and_protected_capsules(self):
        raw = "CANDIDATE='literal CANDIDATE'\nORACLE={'CANDIDATE': 'exact'}\nvalue=CANDIDATE\n"
        value = post.rename_source_scalar(raw)
        self.assertIn("CURRENT_VIEW_CANDIDATE_SOURCE='literal CANDIDATE'", value)
        self.assertIn('value=CURRENT_VIEW_CANDIDATE_SOURCE', value)
        self.assertEqual(capsules(raw), capsules(value))

    def test_foreign_configuration_refused_before_guest_operation(self):
        with patch.object(post.role, 'pinned', return_value='def foreign_configuration(): pass\n'):
            with self.assertRaises(ValueError):
                post.payload()

    def test_only_genuine_unused_placement_qualifies(self):
        good = {'actualExit': 0, 'sourceQualified': True, 'currentApprovalEpochChanged': False}
        post.qualify_placement(good)
        for key, value in [('actualExit', False), ('actualExit', 1),
                           ('sourceQualified', 1), ('sourceQualified', False),
                           ('currentApprovalEpochChanged', 0), ('currentApprovalEpochChanged', True)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                post.qualify_placement({**good, key: value})


if __name__ == '__main__':
    unittest.main()
