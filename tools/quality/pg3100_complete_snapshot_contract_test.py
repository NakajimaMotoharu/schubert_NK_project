"""Independent eleven-key snapshot oracle including real native read, not baseline filtering."""
import ast
import copy
import json
from pathlib import Path
import pathlib
import unittest
from pyflakes.api import check
import pg3080_retained_parent_resume_sources as failed
import pg3100_full_native_resume_sources as fixed
import pg3104_full_native_resume_dispatch as dispatch
import pg3106_full_native_resume_post as post
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema


def returned(raw):
    capture = next(n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef) and n.name == 'capture_data')
    return next(n.value for n in ast.walk(capture) if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict))


class Snapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = fixed.sources()

    def test_pre_fix_missing_native_and_full_independent_projection(self):
        old = returned(failed.sources()['pg3080_native_refs.py'])
        self.assertEqual(10, len(old.keys))
        self.assertFalse(any(k.value == 'native' for k in old.keys))
        value = returned(self.values['pg3100_native_refs.py'])
        expected_keys = {'units', 'configuration', 'rows', 'pid1', 'startup', 'originals', 'backup', 'extraDurable', 'unitFilesActual', 'runtime', 'native'}
        self.assertEqual(expected_keys, {k.value for k in value.keys})
        native = {'/run/schubert-nk/pt-coverage/parent/parent.exec': {'metadata': [28, 6000, 0, 0, 0o100600, 1, 3, 100, 100], 'sha256': 'a' * 64}}
        trees = {'/fixture/startup': {'startup': 'independent'}, '/var/lib/schubert-nk/maintenance': {'original': 'independent'}, '/srv/schubert-nk/backup': {'backup': 'independent'}, '/run/schubert-nk/pt-coverage': copy.deepcopy(native)}
        calls = []
        def tree(path):
            calls.append(str(path))
            return copy.deepcopy(trees[str(path)])
        scope = {'units': {'unit': 'fixed'}, 'cfg': {'config': 'fixed'}, 'data': {'table': []}, 'j': [{'pid1': 'fixed'}], 'startup': Path('/fixture/startup'), 'extra': {'durable': {}}, 'file_entries': {'fixedUnit': []}, 'runtime': {'originalParent': 'fixed'}, 'pathlib': pathlib, 'tree': tree}
        expected = {'units': {'unit': 'fixed'}, 'configuration': {'config': 'fixed'}, 'rows': {'table': []}, 'pid1': [{'pid1': 'fixed'}], 'startup': {'startup': 'independent'}, 'originals': {'original': 'independent'}, 'backup': {'backup': 'independent'}, 'extraDurable': {'durable': {}}, 'unitFilesActual': {'fixedUnit': []}, 'runtime': {'originalParent': 'fixed'}, 'native': native}
        code = compile(ast.Expression(value), '<exact complete snapshot return>', 'eval')
        self.assertEqual(expected, eval(code, scope))
        self.assertEqual(['/fixture/startup', '/var/lib/schubert-nk/maintenance', '/srv/schubert-nk/backup', '/run/schubert-nk/pt-coverage'], calls)
        trees['/run/schubert-nk/pt-coverage'][next(iter(native))]['sha256'] = 'b' * 64
        actual = eval(code, scope)
        self.assertNotEqual(expected['native'], actual['native'])
        def failed_native(path):
            if str(path) == '/run/schubert-nk/pt-coverage':
                raise OSError('independent native read unavailable')
            return tree(path)
        with self.assertRaises(OSError):
            eval(code, {**scope, 'tree': failed_native})
        self.assertTrue('require(set(prior) == set(first) and same_value(first, prior))' in self.values['pg3100_native_refs.py'])

    def test_whole_dispatch_post_and_native_getter_are_not_omitted(self):
        raw = dispatch.source()
        for value in ['pg3102-frozen-v1.safe.json', 'Pg3100FreshResumePreparation', 'pg3104']:
            self.assertTrue(value in raw, value)
        for value in ['pg3084', 'pg3082', 'pg3080']:
            self.assertTrue(value not in raw, value)
        original = json.loads((W / 'pg3096-recovered-native-schema-full-post-v1/manifest.safe.json').read_bytes())
        seals = {n: original['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = post.payload(seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="sealed"\n' + raw, '<all11 corrected full post>'))
        for value in ['pg3104-full-native-resume-preparation-v1', 'zz-pg3100-once-resume.conf', 'retainedOriginalParent', 'len(rows) == 24']:
            self.assertTrue(value in raw, value)


if __name__ == '__main__':
    unittest.main()
