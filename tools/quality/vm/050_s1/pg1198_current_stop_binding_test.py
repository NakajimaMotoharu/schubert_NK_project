"""Independent completed D5/current full seal/generation rejection tests."""
import copy
import unittest
import pg1198_current_stop_binding as p


def fixture():
    return {'actualExit': 0, 'productionSource': p.SOURCE,
        'batchRun': '343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
        'cutoff': '2026-10-10T12:40:27.396847Z', 'activation': 'ada3f7ff-8287-48d7-9ba9-5cce71f61bd3',
        'genuineCompletion': {'genuinePid1StartDone': True, 'genuineRootDone': True, 'endMonotonicUs': 52530445203},
        'beforeSha256': p.BEFORE, 'parentEndedUTC': '2026-10-10T17:37:58.505406Z',
        'ownedUnits': {u: {'MainPID': pid, 'InvocationID': inv, 'ActiveState': 'active', 'SubState': 'running'}
                       for u, (pid,inv) in {'caddy.service':('528966','1037150931c04cb6b64b249c0cf916c3'),
                         'schubert-nk-web.service':('526861','898429f0e6a64d4fa7a6c07e4473fe8a'),
                         'schubert-nk-api.service':('525675','bfae0cf915c74f7bbf35a7a1ec4f8cd9'),
                         'artemis.service':('441175','c874395201b94ae7b144e3a6bb2d3b8e')}.items()}}


class CurrentStopTest(unittest.TestCase):
    def test_whole_generated_current_closure_and_live_functions(self):
        v = p.generate(fixture())
        j = v['Pg1198NativeStop.java']
        for s in [p.SOURCE, p.DIGEST, 'PG1068', 'lease.confirmClosed()', 'maxGapNanos', 'cbca8738-3b24-4090-b77c-bf029677cdd6']:
            self.assertTrue(s in j, s)
        r = v['pg1198_native_refs.py']
        for s in [p.ROOT, 'stable_journal.project(journal)', 'parent-journal-read-', 'output_bound(rp.returncode,len(rp.stdout))', 'extraDurable', 'unitFilesActual']:
            self.assertTrue(s in r, s)
        env = {};exec(v['pg1198_row_bound.py'], env)
        env['output_bound'](0, 34115986)
        for rc, size in [(1, 1), (0, 67108865), (0, 0), (False, 1), (0, None)]:
            with self.assertRaises(ValueError): env['output_bound'](rc, size)
        env = {};exec(v['pg1198_stable_journal.py'], env)
        self.assertEqual(env['project'](b'{"__CURSOR":"fixed","a":"1","b":"2"}\n'), env['project'](b'{"b":"2","a":"1","__CURSOR":"fixed"}\n'))
        for raw in v.values():
            for old in ['eeae04ea-713c-4f2d-888d-358fb4bed274', p.old.SOURCE, 'cc9ed874', 'PG932', 'Pg963']:
                self.assertFalse(old in raw, old)

    def test_fixed_seal_source_completion_and_generation_rejected(self):
        for key, value in [('actualExit', 143), ('productionSource', '0'*40), ('beforeSha256', '0'*64), ('parentEndedUTC', None), ('batchRun', None), ('activation', None)]:
            f=fixture();f[key]=value
            with self.assertRaises((ValueError, TypeError)):p.generate(f)
        for key,value in [('endMonotonicUs', 51172132517), ('endMonotonicUs',52972132519), ('genuineRootDone',False), ('genuinePid1StartDone',False)]:
            f=fixture();f['genuineCompletion'][key]=value
            with self.assertRaises(ValueError):p.generate(f)
        for key,value in [('MainPID','0'), ('MainPID','525676'), ('InvocationID',''), ('InvocationID','a'*32), ('ActiveState','inactive'), ('SubState','exited')]:
            f=fixture();f['ownedUnits']['schubert-nk-api.service'][key]=value
            with self.assertRaises(ValueError):p.generate(f)


if __name__ == '__main__':unittest.main()
