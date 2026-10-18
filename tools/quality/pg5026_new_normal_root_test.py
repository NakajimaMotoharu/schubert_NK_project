"""Independent a2ecc ordinary-entry invariants; no actual Root or permit fixture."""
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg5016_new_current_readonly as current
import pg5018_new_current_same_peer_observer as observer
import pg5032_new_day_query_preflight as oracle
import pg5022_new_normal_root_once as entry
import pg5024_new_normal_live_binding as binding


class NewNormalRoot(unittest.TestCase):
    def test_current_context_strict_and_full80_capacity_no_old_credit(self):
        raw, digest = current.payload(), current.context()
        for marker in (current.SOURCE, current.BOM, current.AFTER, digest,
                       "'native80Preserved':True", "'newRootNotStarted':True",
                       "'oldNativeCredit':False", '12884901888'):
            self.assertIn(marker, raw)
        self.assertEqual(0, check(raw, '<fresh currenta2ecc>'))
        original = json.loads((current.post.role.W / current.post.SLOT / 'manifest.safe.json').read_bytes())
        for key, value in [('productionSource', current.post.role.CURRENT),
                           ('originalBackupNative80Preserved', False), ('newSourceParentNotStarted', False),
                           ('newTenReferencesReturnedNormally', False)]:
            bad = copy.deepcopy(original)
            bad['result'][key] = value
            with patch.object(current.json, 'loads', return_value=bad), self.assertRaises(ValueError):
                current.context()

    def test_four_observer_files_same_source_peer_and_lifetime(self):
        values, ns = observer.files(), observer.namespace()
        self.assertEqual(observer.SOURCE, ns['SOURCE'])
        self.assertEqual(observer.BOM, ns['DIGEST'])
        self.assertEqual(values, ns['files']())
        self.assertEqual({'pg5018_watch_parent.py', 'pg457_stable_actor.py',
                          'pg462_observer_identity.py', 'pg4216_same_peer_observer_manager.py'}, set(values))
        for name, raw in values.items():
            self.assertEqual(0, check(raw, name))
            compile(raw, name, 'exec')
        for marker in ('reader.read(UNITS[role])', 'observerTenMetadataRefsNormalClose'):
            self.assertIn(marker, values['pg5018_watch_parent.py'])
        self.assertIn('pg5014-ssc304-publication-independent-post-v1', observer.source())
        self.assertIn('PG4980', observer.source())
        self.assertNotIn('PG4860', observer.source())

    def test_preflight_exact_before_and_current_no_old_or_key_export(self):
        raw = oracle.payload()
        self.assertEqual(0, check(raw, '<actual current independent window>'))
        for marker in (current.AFTER, current.context(), current.BOM, 'now+datetime.timedelta(hours=2)',
                       "'rootStartIssued':False", "'plaintextLogged':False", "'dbOrClockChanged':False"):
            self.assertIn(marker, raw)
        self.assertIn(r"KEY[:]=b'\0'*len(KEY)", raw)
        self.assertNotIn('pg4886-ssc301-302-publication-independent-post-v1', raw)

    def test_source_window_and_before_sha_mandatory(self):
        now = datetime.datetime(2026, 10, 18, 0, 0, tzinfo=datetime.timezone.utc)
        proof = {'actualExit': 0, 'source': entry.SOURCE, 'result': {'beforeSha256': 'a' * 64,
                 'dbOrClockChanged': False, 'rootStartIssued': False, 'projections': [
                 {'cutoff': now.isoformat(), 'independentApplicability': True},
                 {'cutoff': (now + datetime.timedelta(hours=2)).isoformat(), 'independentApplicability': True}]}}
        entry.oracle_applicable(proof, now, 'a' * 64)
        for key, value in [('actualExit', False), ('source', 'f' * 40)]:
            with self.assertRaises(ValueError):
                entry.oracle_applicable({**proof, key: value}, now, 'a' * 64)
        for key, value in [('dbOrClockChanged', True), ('rootStartIssued', True),
                           ('beforeSha256', 'b' * 64), ('projections', [])]:
            bad = copy.deepcopy(proof)
            bad['result'][key] = value
            with self.assertRaises(ValueError):
                entry.oracle_applicable(bad, now, 'a' * 64)
        for shift in (-1, 3):
            with self.assertRaises(ValueError):
                entry.oracle_applicable(proof, now + datetime.timedelta(hours=shift), 'a' * 64)

    def test_durable_reservation_manifest_barrier_and_original1800_budget(self):
        nodes = ast.parse(entry.action()).body
        index = next(i for i, n in enumerate(nodes) if isinstance(n, ast.Expr)
                     and isinstance(n.value, ast.Call) and ast.unparse(n.value.func) == 'persist'
                     and n.value.args[0].value == 'external-start-guard.private.json')
        block = ast.Module(body=nodes[index - 1:index + 1], type_ignores=[])
        literal = b'{"independent":"fixed bytes"}\n'
        digest = hashlib.sha256(literal).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'manifest'
            path.write_bytes(literal)
            for data, sha, valid in ((literal, digest, True), (b'foreign', digest, False), (literal, '0' * 64, False)):
                records = []
                def require(value):
                    if value is not True:
                        raise ValueError('barrier refused')
                ns = {'manifest_path': path, 'manifest': data, 'sha': sha, 'hashlib': hashlib,
                      'require': require, 'data': {'source': {'commit': entry.SOURCE}},
                      'summary': {'genuineParentDone': True, 'completionCode': 10}, 'watch': {'pid': 123},
                      'persist': lambda name, value: records.append((name, value))}
                if valid:
                    exec(compile(block, '<actual durable reservation>', 'exec'), ns)
                    self.assertEqual(1, len(records))
                    guard = records[0][1]
                    self.assertTrue(guard['previousRootDataOnly'])
                    self.assertFalse(guard['replayAllowed'])
                    self.assertEqual(1800, guard['originalBudgetSeconds'])
                    self.assertEqual(digest, guard['manifestSha256'])
                    json.dumps(guard)
                else:
                    with self.assertRaises(ValueError):
                        exec(compile(block, '<actual durable reservation>', 'exec'), ns)
                    self.assertEqual([], records)

    def test_one_start_and_all80_success_only_after_normal_refs(self):
        hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in observer.files().items()}
        raw = entry.payload(hashes)
        self.assertEqual(0, check(raw, '<actuala2ecc whole ordinary Root>'))
        calls = [ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse(entry.action()))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and ast.unparse(n.func) == 'subprocess.run']
        self.assertEqual([['/usr/bin/systemctl', 'start', '--no-block', 'schubert-nk-morning-controller.service']], calls)
        for marker in ('require(len(records)==80)', 'previousRootDataOnly', "'--resume'not in declaration", entry.SOURCE, entry.BOM):
            self.assertIn(marker, raw)
        self.assertNotIn("'parentExit':143", raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"), raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index('for unit in reversed(refs):manager.UnrefUnit(unit)'), raw.index('current.update(observedUTC='))

    def test_live_binding_new_once_current_and_negative_historical_ids(self):
        raw = binding.body()
        self.assertEqual(0, check('SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n' + raw, '<actual binding>'))
        self.assertEqual(entry.SLOT, binding.ONCE)
        self.assertIn('0.1.0-PG4980', raw)
        self.assertNotIn('pg4892-new-normal-root-once-v1', raw)
        self.assertIn('fff841d9-2554-4680-b17d-9548bfa79cbb', raw)
        self.assertIn("unit['InvocationID']!='b414b0e1e5ac47e8b5fb8c5ae3d94348'", raw)
        for p in (current.__file__, observer.__file__, oracle.__file__, entry.__file__, binding.__file__, __file__):
            self.assertEqual(0, checkPath(p))


if __name__ == '__main__':
    unittest.main()
