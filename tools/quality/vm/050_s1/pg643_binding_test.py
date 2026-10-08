"""Independent literal new-source post bindings; old fixed content not imported."""
import unittest
import ast
import types
from pg642_stop_binding_test import fixture
from pg643_terminal_final import payload, SEAL


class Binding(unittest.TestCase):
    def test_complete_fresh_post_scope(self):
        seals = {name: str(i+1)*64 for i, name in enumerate(
            ('before.private.json', 'after.private.json', 'complete.private', 'parent.private.jsonl'))}
        source = payload(fixture(), seals); compile(source, '<fixed current post>', 'exec')
        for text in ('pg642-native-stop-v1', 'pg642-native-tools-v1', 'pg643-terminal-final-v2',
                     'pg631-manifest.sig', "summary=e['completed'](receipt_rows,strict(done_path,0o600,141))", "native==snapshot()", 'manager.UnrefUnit(u)',
                     'bus.close()', "rows==after['rows']and len(rows)==24", "show(u,configuration_fields())==after['configuration'][u]",
                     "'startsStopsReloadsSqlWrites':0"):
            self.assertIn(text, source)
        for old in ('pg611', 'PG600', '23b14a44', '1207482', '87761979588', '19b7e618'):
            self.assertNotIn(old, source)

    def test_atime_only_is_not_security_change(self):
        tree = ast.parse(SEAL); node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'metadata9')
        env = {}; exec(compile(ast.Module(body=[node], type_ignores=[]), '<metadata contract>', 'exec'), env)
        fields = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        a = types.SimpleNamespace(**{k:i for i,k in enumerate(fields)}, st_atime=1)
        b = types.SimpleNamespace(**vars(a)); b.st_atime = 99
        self.assertEqual(env['metadata9'](a), env['metadata9'](b))
        for k in fields:
            b = types.SimpleNamespace(**vars(a)); setattr(b, k, 99)
            with self.subTest(k=k): self.assertNotEqual(env['metadata9'](a), env['metadata9'](b))


if __name__ == '__main__': unittest.main()
