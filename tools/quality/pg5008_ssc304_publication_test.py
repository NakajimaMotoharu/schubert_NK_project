"""Independent finite-role/transport/oracle checks; no VM or actual permit fixture."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
from bundle_hash_contract import require_bound
from pg4992_ssc304_unused_post_test import capsules
import pg5008_ssc304_publication_sources as role
import pg5010_ssc304_publication_compile as compiler
import pg5012_ssc304_publication_dispatch as dispatch
import pg5014_ssc304_publication_post as post


class FinitePublication(unittest.TestCase):
    def test_actual_ro_and_all24_roles_capsules_and_current_abi(self):
        self.assertTrue(role.qualify()['native80Preserved'])
        ro, values = role.ro.sources(), compiler.generated()
        self.assertEqual(24, len(values))
        for suffix in ('parent_receipt', 'warning_parent_projection'):
            self.assertEqual(capsules(ro['pg5000_' + suffix + '.py']),
                             capsules(values['pg5008_' + suffix + '.py']))
        self.assertTrue(require_bound(values['pg5008_native_refs.py'],
                                     compiler.ro_compile.sha(compiler.ro_compile.PRIOR / 'bundle.safe.json')))
        for marker in ('pg5010-frozen-v1.safe.json', 'pg4988-frozen-v1.safe.json',
                       "('transition','TransitionTest')", 'pg4860-release-v1/api/api.jar'):
            self.assertIn(marker, compiler.compiler())
        for name in ('pg1083_cold_publication_contract.py', 'pg1088_cold_exchange_io.py',
                     'pg1090_cold_finite_capture.py', 'pg2441_ordinary_exchange_io.py'):
            self.assertIn(name, values)

    def test_incomplete_foreign_bool_or_oldnative_ro_never_qualifies(self):
        original = json.loads((role.W / 'pg5006-ssc304-ro-independent-post-v1/manifest.safe.json').read_bytes())
        for key, value in [('candidateHostReadonlyVerified', False), ('candidateSource', role.CURRENT),
                           ('currentSource', role.SOURCE), ('candidateManifestSha256', '0' * 64),
                           ('newTenReferencesReturnedNormally', False), ('actualExit', False), ('native80Preserved', False)]:
            bad = copy.deepcopy(original)
            bad['result'][key] = value
            with patch.object(role.ro, 'qualify'), patch.object(role.json, 'loads', return_value=bad):
                with self.assertRaises(ValueError):
                    role.qualify()

    def test_actual_entry_kind_full_stage_contract_and_single_gate(self):
        fixture = {'actualExit': 0, 'productionSource': role.CURRENT, 'candidateSource': role.SOURCE,
                   'candidateManifestSha256': role.BOM, 'fileHashes': {n: 'a' * 64 for n in compiler.generated()}}
        fixture['fileHashes'].update({role.CLASS + '.class': 'b' * 64, 'Pg5008TransitionTest.class': 'c' * 64})
        dispatch.qualify_fixed(fixture)
        for key, value in [('actualExit', False), ('productionSource', role.SOURCE),
                           ('candidateSource', role.CURRENT), ('candidateManifestSha256', '0' * 64)]:
            with self.assertRaises(ValueError):
                dispatch.qualify_fixed({**fixture, key: value})
        bad = copy.deepcopy(fixture)
        bad['fileHashes']['Pg5000CandidateRo.class'] = '0' * 64
        with self.assertRaises(ValueError):
            dispatch.qualify_fixed(bad)
        raw = dispatch.source()
        for marker in ('pg5010-frozen-v1.safe.json', 'pg5012-stage-v1.exit', '0.1.0-PG4860',
                       'Pg5008TransitionTest', "['stage'],['activate']", 'qualify_fixed(fixed)'):
            self.assertIn(marker, raw)
        self.assertEqual(1, raw.count('with management_gate('))
        self.assertIn(dispatch.GUEST, dispatch.STAGE)
        self.assertIn(dispatch.REMOTE, dispatch.STAGE)
        # BUG1402/YKT1166: check every emitted transport literal, not just paths.
        self.assertIn('0.1.0-PG4860', dispatch.STAGE)
        self.assertIn('/home/ubuntu/pg5012-ssc304-publication-stage-v1/pg5008-ssc304-publication-tools-v1.tar', dispatch.STAGE)
        for old in ('0.1.0-PG4702', 'pg4880', 'pg4884', 'pg4872'):
            self.assertNotIn(old, dispatch.STAGE)
        with patch.object(dispatch.sys, 'argv', ['tool', 'start']), patch.object(dispatch, 'authenticate_host') as auth:
            with self.assertRaises(ValueError):
                dispatch.main()
        auth.assert_not_called()

    def test_all_phase_independent_source_fixture_and_durable_sql_before_parse(self):
        original = Path.read_bytes
        target = role.W / 'pg5010-frozen-v1.safe.json'
        fixture = {'actualExit': 0, 'fileHashes': {'FIXTURE_SOURCE_ONLY': hashlib.sha256(b'fixture').hexdigest()}}
        def read(path):
            return json.dumps(fixture).encode() if path == target else original(path)
        with patch.object(Path, 'read_bytes', read):
            raw = post.payload()
        self.assertEqual(0, check(raw, '<explicit non-runtime finite source fixture>'))
        self.assertIn("old_after={**after,'native':expected['native']}", raw)
        for marker in (role.SOURCE, role.BOM, 'pg4980-manifest.sig', post.FULL_BEFORE, post.FULL_SHA,
                       'len(phases)>=7', "oracle['PHASES']", "for stamp,phase,observed in phases:oracle['verify']",
                       'originalBackupNative80Preserved', 'oldNativeNotAppliedToNewSource',
                       "'newSourceParentNotStarted':True"):
            self.assertIn(marker, raw)
        tree = ast.parse(raw)
        reader = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'read_rows')
        body = ast.unparse(reader)
        self.assertLess(body.index('sql-read-'), body.index('json.loads(line)'))
        self.assertLess(body.index('os.fsync(fd)'), body.index('json.loads(line)'))
        held = next(n for n in tree.body if isinstance(n, ast.Try) and 'UnrefUnit' in ast.unparse(n.finalbody))
        self.assertGreater(tree.body[-1].lineno, held.end_lineno)
        for p in (role.__file__, compiler.__file__, dispatch.__file__, post.__file__, __file__):
            self.assertEqual(0, checkPath(p))


if __name__ == '__main__':
    unittest.main()
