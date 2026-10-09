"""Sealed owner AST + independent current genuine PID1/DONE literals; no VM grant."""
import datetime
import types
import unittest
from pathlib import Path
import pg717_sources as p

R = Path(__file__).resolve().parent


def suite():
    owner = p.bind(p.previous.bind((R / 'pg624_owner_namespace_test.py').read_text()))
    owner = owner.replace("(R/'pg717_completed_refs.py').read_text()", repr(p.refs()))
    mod = types.ModuleType('sealed_current_owner'); mod.__file__ = str(R / 'pg717_owner_receipt_test.py')
    exec(compile(owner, '<actual sealed owner with explicit host proc fixture>', 'exec'), mod.__dict__)
    result = unittest.TestSuite(); result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(mod.Test))
    result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Receipt))
    return result


class Receipt(unittest.TestCase):
    def test_actual_current_literals_and_foreign_missing_time_refusals(self):
        env = {'datetime': datetime}; exec(compile(p.receipt(), '<pure genuine parent contract>', 'exec'), env)
        base = {'_BOOT_ID': 'cc9ed8747f4f450ea1888de1e42c8441', '_PID': '1', '_UID': '0', '_COMM': 'systemd',
                'UNIT': 'schubert-nk-morning-controller.service', 'INVOCATION_ID': '6b3dd954959c43c1bbac2164ec9d0c6b',
                '__MONOTONIC_TIMESTAMP': '121040711116', '__REALTIME_TIMESTAMP': '1791508338000000'}
        rows = [{**base, '__CURSOR': 'literal-a', 'MESSAGE_ID': '39f53479d3a045ac8e11786248231fbf', 'JOB_ID': '122726', 'JOB_TYPE': 'start', 'JOB_RESULT': 'done'},
                {**base, '__CURSOR': 'literal-b', 'MESSAGE_ID': '7ad2d189f7e94e70a38c781354912448'}]
        done = b'NKDONE1\n8633b77f-77dc-4a78-88b4-41165f159b43\n2026-10-09T00:43:10.150245Z\nc6815985-26c5-4f5f-aed0-abc81fa8f71e\n2026-10-09T01:12:17.452418Z\n0\n'
        self.assertEqual(env['completed'](rows, done)['endMonotonicUs'], 121040711116)
        for key in rows[0]:
            bad = [{**rows[0], key: None}, rows[1]]
            with self.subTest(key=key), self.assertRaises(ValueError): env['completed'](bad, done)
        for bad in (None, [], rows + rows):
            with self.assertRaises(ValueError): env['completed'](bad, done)
        for bad in (None, done.replace(b'8633b77f', b'old3b77f'), done.replace(b'\n0\n', b'\n1\n')):
            with self.assertRaises(ValueError): env['completed'](rows, bad)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(suite())
    assert result.testsRun == 4
    raise SystemExit(0 if result.wasSuccessful() else 1)
