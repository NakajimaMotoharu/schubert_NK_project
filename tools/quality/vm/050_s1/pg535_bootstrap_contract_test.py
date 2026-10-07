"""Independent literal18/30s/footprint/DBscope ordering vectors; VM actions0, Production PT0."""
import ast
import copy
import pathlib
import os
import tempfile
import unittest

from pg535_bootstrap_contract import normal20, same_terminal_cohort, credential_tree, native_tree, retire_no_replace, UNIT


def literal20():
    return {'Id': 'schubert-nk-bootstrap-admin.service', 'LoadState': 'loaded',
            'ActiveState': 'inactive', 'SubState': 'dead', 'Job': '', 'MainPID': '0',
            'ControlPID': '0', 'InvocationID': 'a' * 32, 'Type': 'oneshot', 'Restart': 'no',
            'RemainAfterExit': 'no', 'Result': 'success', 'ExecMainCode': '1', 'ExecMainStatus': '20',
            'ExecMainStartTimestampMonotonic': '100', 'ExecMainExitTimestampMonotonic': '200',
            'KillMode': 'control-group', 'SendSIGKILL': 'no'}


def directory(uid=0, gid=0):
    return {'metadata': [17, 23, uid, gid, 0o40700, 2, 4096, 100, 100], 'sha256': None}


class BootstrapContractTest(unittest.TestCase):
    def test_probe_run_and_all_artifacts_use_one_independent_literal(self):
        source = (pathlib.Path(__file__).parent / 'pg535_bootstrap_snapshot_probe_v2.py').read_text()
        module = ast.parse(source)
        run = [n.value.value for n in module.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'RUN' for t in n.targets)]
        self.assertEqual(['PG535-snapshot-probe-v2'], run)
        self.assertIn("'run':RUN", source)
        for suffix in ('.private.log', '.exit', '.source.json'):
            self.assertIn("RUN.lower()+'" + suffix + "'", source)
        self.assertNotIn('probe-v1', source)
        self.assertNotIn('probe-v3', source)

    def test_retirement_is_atomic_no_replace_and_never_overwrites_existing_preservation(self):
        for result in (0, -1):
            calls = []
            def syscall(*args):
                calls.append(args)
                return result
            if result == 0:
                retire_no_replace(3, 'bootstrap-admin-password', 4, syscall)
            else:
                with self.assertRaises(ValueError):
                    retire_no_replace(3, 'bootstrap-admin-password', 4, syscall)
            self.assertEqual([(3, b'bootstrap-admin-password', 4,
                               b'bootstrap-admin-password.retired.private', 1)], calls)
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            source = root / 'source'
            target = root / 'preserved'
            source.mkdir()
            target.mkdir()
            name = 'bootstrap-admin-username'
            (source / name).write_bytes(b'independent synthetic fixture')
            (target / (name + '.retired.private')).write_bytes(b'prior preserved fixture')
            a = os.open(source, os.O_RDONLY | os.O_DIRECTORY)
            b = os.open(target, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(ValueError):
                    retire_no_replace(a, name, b)
                self.assertEqual(b'independent synthetic fixture', (source / name).read_bytes())
                self.assertEqual(b'prior preserved fixture', (target / (name + '.retired.private')).read_bytes())
                fresh = 'bootstrap-admin-password'
                (source / fresh).write_bytes(b'new synthetic fixture')
                old_inode = (source / fresh).stat().st_ino
                retire_no_replace(a, fresh, b)
                self.assertFalse((source / fresh).exists())
                self.assertEqual(b'new synthetic fixture', (target / (fresh + '.retired.private')).read_bytes())
                self.assertEqual(old_inode, (target / (fresh + '.retired.private')).stat().st_ino)
            finally:
                os.close(a)
                os.close(b)

    def test_normal20_all18_fields_and_null_unknown_missing(self):
        self.assertTrue(normal20(literal20()))
        for key in literal20():
            for fault in ('null', 'missing', 'foreign', 'type'):
                bad = literal20()
                if fault == 'missing':
                    del bad[key]
                else:
                    bad[key] = {'null': None, 'foreign': 'foreign', 'type': 0}[fault]
                with self.subTest(key=key, fault=fault):
                    self.assertFalse(normal20(bad))
        for bad in (None, {}, [], {**literal20(), 'foreign': 'x'}):
            self.assertFalse(normal20(bad))

    def test_exact_unit30s_and_canonical_timestamp_receipt(self):
        for start, end, result in (('0', '100', False), ('100', '99', False),
                                   ('100', '100', True), ('100', '30000100', True),
                                   ('100', '30000101', False), ('0100', '200', False),
                                   ('١٠٠', '200', False), ('100', '9223372036854775808', False)):
            self.assertEqual(result, normal20({**literal20(), 'ExecMainStartTimestampMonotonic': start,
                                               'ExecMainExitTimestampMonotonic': end}))
        for key, values in (('InvocationID', ['', '0' * 32, 'F' * 32]),
                            ('ExecMainCode', ['0', '2']), ('ExecMainStatus', ['0', '50', '70', '143']),
                            ('Result', ['timeout', 'signal', 'exit-code'])):
            for value in values:
                self.assertFalse(normal20({**literal20(), key: value}))

    def test_only_one_fresh_bootstrap_generation_changes_cohort(self):
        old = {UNIT: {**literal20(), 'InvocationID': '', 'ExecMainCode': '0', 'ExecMainStatus': '0'},
               'caddy.service': {**literal20(), 'Id': 'caddy.service'}}
        same_terminal_cohort(old, copy.deepcopy(old))
        current = {**old, UNIT: literal20()}
        same_terminal_cohort(old, current, literal20())
        for bad in ({**current, 'foreign.service': {}},
                    {**current, 'caddy.service': {**old['caddy.service'], 'MainPID': '77'}},
                    {**current, UNIT: {**literal20(), 'InvocationID': 'b' * 32}}):
            with self.assertRaises(ValueError):
                same_terminal_cohort(old, bad, literal20())
        with self.assertRaises(ValueError):
            same_terminal_cohort(current, current, literal20())

    def test_two_credential_sources_and_only_parent_directory_time_changes(self):
        root = '/etc/schubert-nk/credentials'
        original = {root: directory(), root + '/db-api-password':
                    {'metadata': [17, 24, 0, 0, 0o100400, 1, 43, 100, 100], 'sha256': 'b' * 64}}
        prepared = {root + '/' + name:
                    {'metadata': [17, 25 + i, 0, 0, 0o100400, 1, 43, 200, 200], 'sha256': 'c' * 64}
                    for i, name in enumerate(('bootstrap-admin-username', 'bootstrap-admin-password'))}
        actual = {**copy.deepcopy(original), **prepared}
        actual[root]['metadata'][7:9] = [200, 200]
        credential_tree(original, actual, prepared)
        credential_tree(original, copy.deepcopy(original), {})
        for bad in ({**actual, root + '/foreign': prepared[root + '/bootstrap-admin-password']},
                    {**actual, root + '/db-api-password': prepared[root + '/bootstrap-admin-password']},
                    {**actual, root: {'metadata': [17, 999, 0, 0, 0o40700, 2, 4096, 100, 100], 'sha256': None}}):
            with self.assertRaises(ValueError):
                credential_tree(original, bad, prepared)
        for key, bad_value in (('metadata', None), ('sha256', 'not-sha')):
            bad = copy.deepcopy(actual)
            bad[root + '/bootstrap-admin-password'][key] = bad_value
            with self.assertRaises(ValueError):
                credential_tree(original, bad, prepared)

    def test_only_fresh_bootstrap_native_file_and_normal_metadata_are_added(self):
        role = '/run/schubert-nk/pt-coverage/ordinary-bootstrap196'
        original = {role: directory(999, 981), '/run/schubert-nk/pt-coverage/parent/parent.exec':
                    {'metadata': [17, 24, 0, 0, 0o100600, 1, 50, 100, 100], 'sha256': 'b' * 64}}
        path = role + '/' + 'a' * 32 + '.terminal.exec'
        added = {'metadata': [17, 25, 999, 981, 0o100600, 1, 50, 200, 200], 'sha256': 'c' * 64}
        actual = {**copy.deepcopy(original), path: added}
        actual[role]['metadata'][7:9] = [200, 200]
        native_tree(original, original)
        native_tree(original, actual, 'a' * 32)
        for index, bad_value in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0o100640),
                                 (5, 2), (6, 4), (6, 16777217), (6, True)):
            bad = copy.deepcopy(actual)
            bad[path]['metadata'][index] = bad_value
            with self.subTest(index=index, value=bad_value), self.assertRaises(ValueError):
                native_tree(original, bad, 'a' * 32)
        for inv in (None, '', '0' * 32, 'F' * 32, 'b' * 32):
            with self.assertRaises(ValueError):
                native_tree(original, actual, inv)
        bad = copy.deepcopy(actual)
        bad['/run/schubert-nk/pt-coverage/parent/parent.exec']['sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            native_tree(original, bad, 'a' * 32)

    def test_prepare_database_closes_before_one_reserved_start_and_fresh_post_database(self):
        here = pathlib.Path(__file__).parent
        java = (here / 'Pg535BootstrapExisting.java').read_text()
        before = java.index('try(var database=open())')
        prepared = java.index('refs.check("prepare")', before)
        close = java.index('PREPARE_DATABASE_SCOPE_CLOSE', prepared)
        start = java.index('refs.check("run")', close)
        after = java.index('try(var database=open())', start)
        retire = java.index('refs.check("retire:', after)
        release = java.index('refs.release()', retire)
        self.assertTrue(before < prepared < close < start < after < retire < release)
        py = (here / 'pg535_bootstrap_existing.py').read_text()
        ast.parse(py)
        self.assertEqual(1, py.count("'start','--no-block',UNIT"))
        self.assertLess(py.index("save('start-reserved.private.json'"), py.index("'start','--no-block',UNIT"))
        self.assertIn('connection(False);snapshot(False)', py)
        self.assertNotIn('pg482-bootstrap-existing', py)
        self.assertNotIn('pg468-active-account.private.json', py)


if __name__ == '__main__':
    unittest.main()
