"""Independent explicit same-run bindings and genuine PID1 boundary fixtures."""
import ast
import datetime
from pathlib import Path
import unittest
from pg640_capture_done import payload


class Binding(unittest.TestCase):
    def test_fixed_current_and_preserved_strict_capture(self):
        code = payload(); compile(code, '<fixed resume capture>', 'exec')
        for literal in ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '0.1.0-PG631',
                        '1522744', '104329', '103062293730', '293d218b06454bd1a8ff350bb93de2d5',
                        '7d381b67-b37b-48c6-99ac-e04a336f887d', "cutoff=='2026-10-08T18:32:42.140966Z'",
                        "summary=env['completed'](pid1,done)", 'after==snapshot()', 'manager.UnrefUnit(u)', 'bus.close()'):
            self.assertIn(literal, code)
        self.assertNotIn("baseline['bounds']", code)
        self.assertNotIn("['systemctl','start'", code)
        self.assertNotIn('p.lstat()==s', code)
        self.assertIn('metadata9(p.lstat())==metadata9(s) and not os.listxattr(p)', code)

    def test_genuine_new_resume_job_not_old_cutoff_budget(self):
        tree = ast.parse((Path(__file__).parent/'pg609_parent_receipt.py').read_text())
        env = dict(datetime=datetime, BOOT='cc9ed8747f4f450ea1888de1e42c8441',
                   INV='293d218b06454bd1a8ff350bb93de2d5', JOB='104329', START=103062293730,
                   RUN='e49243d5-de84-4714-8612-6912ddc17e9e', CUTOFF='2026-10-08T18:32:42.140966Z',
                   ACT='7d381b67-b37b-48c6-99ac-e04a336f887d')
        exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), '<strict oracle>', 'exec'), env)
        base = {'_BOOT_ID': env['BOOT'], '_PID': '1', '_UID': '0', '_COMM': 'systemd',
                'UNIT': 'schubert-nk-morning-controller.service', 'INVOCATION_ID': env['INV'],
                '__MONOTONIC_TIMESTAMP': '103062393730', '__REALTIME_TIMESTAMP': '1791490621000000'}
        rows = [dict(base, __CURSOR='first', MESSAGE_ID='39f53479d3a045ac8e11786248231fbf', JOB_ID='104329', JOB_TYPE='start', JOB_RESULT='done'),
                dict(base, __CURSOR='second', MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        done = b'NKDONE1\ne49243d5-de84-4714-8612-6912ddc17e9e\n2026-10-08T18:32:42.140966Z\n7d381b67-b37b-48c6-99ac-e04a336f887d\n2026-10-08T20:17:00.000000Z\n0\n'
        self.assertEqual(env['completed'](rows, done)['elapsedSeconds'], .1)
        for change in ({'INVOCATION_ID': 'old'}, {'JOB_ID': 'old'}, {'JOB_RESULT': 'failed'},
                       {'__MONOTONIC_TIMESTAMP': '104862293731'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                env['completed']([dict(rows[0], **change), rows[1]], done)


if __name__ == '__main__': unittest.main()
