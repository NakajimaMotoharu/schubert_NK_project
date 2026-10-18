"""RO role contract, all namespace/capsules/current ABI, independent post boundaries."""
import ast
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
from bundle_hash_contract import require_bound
from pg4992_ssc304_unused_post_test import capsules
import pg5000_ssc304_ro_sources as role
import pg5002_ssc304_ro_compile as compiler
import pg5004_ssc304_ro_dispatch as dispatch
import pg5006_ssc304_ro_post as post


class Ro(unittest.TestCase):
    def test_actual_full80_all18_capsules_and_actual_current_abi(self):
        self.assertTrue(role.qualify()['native80Preserved'])
        normal, values = role.unused.sources(), compiler.generated()
        self.assertEqual(18, len(values))
        for suffix in ('parent_receipt', 'warning_parent_projection'):
            self.assertEqual(capsules(normal['pg4986_' + suffix + '.py']),
                             capsules(values['pg5000_' + suffix + '.py']))
        digest = compiler.sha(compiler.PRIOR / 'bundle.safe.json')
        self.assertTrue(require_bound(values['pg5000_native_refs.py'], digest))
        for name, raw in values.items():
            if name.endswith('.py'):
                self.assertEqual(0, check(raw, '<actual RO ' + name + '>'))
        for marker in ('pg4988-frozen-v1.safe.json', 'pg4860-release-v1/api/api.jar',
                       'pg4860-release-v1/operations/batch.jar'):
            self.assertIn(marker, compiler.compiler())

    def test_reject_foreign_or_incomplete_post(self):
        original = json.loads((role.W / 'pg4992-ssc304-unused-post-v1/manifest.safe.json').read_bytes())
        for key, value in [('candidateSource', role.CURRENT), ('currentSource', role.SOURCE),
                           ('native80Preserved', False), ('newTenReferencesReturnedNormally', False),
                           ('candidateManifestSha256', '0' * 64), ('actualExit', False)]:
            bad = copy.deepcopy(original)
            bad['result'][key] = value
            with patch.object(role.unused, 'qualify'), patch.object(role.json, 'loads', return_value=bad):
                with self.assertRaises(ValueError):
                    role.qualify()

    def test_explicit_actions_actual_current_and_single_gate(self):
        raw = dispatch.entry_source()
        for marker in ('pg5002-frozen-v1.safe.json', 'pg5004-stage-v1.exit',
                       '0.1.0-PG4860', 'Pg5000OriginalTupleTest', "['stage'],['prepare-ro']"):
            self.assertIn(marker, raw)
        self.assertEqual(1, raw.count('with management_gate('))
        self.assertIn(dispatch.GUEST, dispatch.STAGE)
        self.assertIn(dispatch.REMOTE, dispatch.STAGE)
        with patch.object(dispatch.sys, 'argv', ['tool', 'activate']), patch.object(dispatch, 'authenticate_host') as auth:
            with self.assertRaises(ValueError):
                dispatch.main()
        auth.assert_not_called()

    def test_ro_mount_receipt_checks_held_and_success_only_after_normal_close(self):
        raw = post.payload()
        self.assertEqual(0, check(raw, '<full80 RO post>'))
        tree = ast.parse(raw)
        scope = next(n for n in tree.body if isinstance(n, ast.Try)
                     and 'manager.UnrefUnit(u)' in ast.unparse(n.finalbody))
        held = ast.unparse(scope.body)
        for marker in ('findmnt', '--mountpoint', '0.1.0-PG4980', role.SAVE,
                       'candidateReadOnlyVerified=true', 'allNewScopesReturnedNormally=true',
                       'json.loads(before) == expected'):
            self.assertIn(marker, held)
        self.assertGreater(tree.body[-1].lineno, scope.end_lineno)
        self.assertIn("'candidateHostReadonlyVerified': True", ast.unparse(tree.body[-1]))
        for p in (role.__file__, compiler.__file__, dispatch.__file__, post.__file__, __file__):
            self.assertEqual(0, checkPath(p))


if __name__ == '__main__':
    unittest.main()
