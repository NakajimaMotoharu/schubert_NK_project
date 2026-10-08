"""Literal new cohort vectors; do not use live receipt to generate expected."""
import copy
import unittest
from pg642_stop_binding import bindings, generate


def fixture():
    return {'actualExit': 0, 'productionSource': '36fe7a0b938489d61d17d49c1c30a6fbbef699d5',
            'batchRun': 'e49243d5-de84-4714-8612-6912ddc17e9e', 'cutoff': '2026-10-08T18:32:42.140966Z',
            'activation': '7d381b67-b37b-48c6-99ac-e04a336f887d', 'beforeSha256': 'f'*64,
            'genuineCompletion': {'genuinePid1StartDone': True, 'genuineRootDone': True, 'endMonotonicUs': 103063293730},
            'parentEndedUTC': '2026-10-08T20:30:00.000000Z',
            'ownedUnits': {u: {'MainPID': str(2000000+i), 'InvocationID': str(i+1)*32,
                              'ActiveState': 'active', 'SubState': 'running'} for i, u in enumerate(
                                  ('caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service', 'artemis.service'))}}


class Binding(unittest.TestCase):
    def test_generated_roles_and_unchanged_order_scope_guards(self):
        out = generate(fixture())
        self.assertEqual(len(out), 8)
        for name, source in out.items():
            if name.endswith('.py'): compile(source, name, 'exec')
        java = out['Pg642NativeStop.java']
        self.assertIn('done.endedAt().equals(java.time.Instant.parse("2026-10-08T20:30:00.000000Z"))', java)
        self.assertNotIn('cutoff().plusSeconds(1800)', java)
        for text in ('MaintenanceFileLock.create().tryExclusive', 'StartupAdmissionFile.create().tryExclusive',
                     'pg_try_advisory_lock(71419602)', 'refs.check("terminal")', 'db.rollback();db.close()',
                     'refs.release()', 'databaseUpdates0=true'):
            self.assertIn(text, java)
        stop = out['pg642_native_owned_stop.py']
        self.assertIn("('2000000','11111111111111111111111111111111')", stop)
        self.assertIn("b'Pg642NativeStop'", stop)
        self.assertIn("103062293730<=int(r['__MONOTONIC_TIMESTAMP'])<=104862293730", stop)
        self.assertIn("unit==h.ORDER[len(stages)]", out['pg642_native_refs.py'])

    def test_foreign_missing_null_and_budget(self):
        for key, value in (('actualExit', 1), ('productionSource', 'old'), ('batchRun', None),
                           ('activation', 'foreign'), ('cutoff', 'new'), ('beforeSha256', None),
                           ('parentEndedUTC', None)):
            v = fixture(); v[key] = value
            with self.subTest(key=key), self.assertRaises((ValueError, KeyError, TypeError)): bindings(v)
        for value in (False, True, None):
            v = fixture(); v['actualExit'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): bindings(v)
        for value in ('2026-10-08T99:99:99.000000Z', '2026-10-08T10:00:00.000000Z'):
            v = fixture(); v['parentEndedUTC'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): bindings(v)
        for value in (103062293729, 104862293731, None, True):
            v = fixture(); v['genuineCompletion']['endMonotonicUs'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): bindings(v)
        for unit in fixture()['ownedUnits']:
            for key in ('MainPID', 'InvocationID', 'ActiveState', 'SubState'):
                v = copy.deepcopy(fixture()); v['ownedUnits'][unit][key] = None
                with self.subTest(unit=unit, key=key), self.assertRaises(ValueError): bindings(v)


if __name__ == '__main__': unittest.main()
