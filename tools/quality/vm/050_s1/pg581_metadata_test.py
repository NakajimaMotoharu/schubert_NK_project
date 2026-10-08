"""Independent stat attribute contract: atime is read observation, not content identity."""
import ast
import pathlib
import types
import unittest


class MetadataContract(unittest.TestCase):
    def test_sealed_after_schema(self):
        module = ast.parse(pathlib.Path(__file__).with_name('pg581_native_counter.py').read_text())
        payload = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        keys = {ast.literal_eval(n.slice) for n in ast.walk(ast.parse(payload))
                if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
                and n.value.id in ('a', 'b') and isinstance(n.slice, ast.Constant)}
        self.assertEqual({'rows', 'pid1', 'units'}, keys)
        self.assertLessEqual(keys, {'backup', 'configuration', 'originals', 'pid1', 'rows', 'startup', 'units'})

    def test_exact_nine_attributes(self):
        module = ast.parse(pathlib.Path(__file__).with_name('pg581_native_counter.py').read_text())
        payload = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        function = next(n for n in ast.parse(payload).body if isinstance(n, ast.FunctionDef) and n.name == 'metadata')
        env = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<actual-metadata>', 'exec'), env)
        fields = ('dev', 'ino', 'uid', 'gid', 'mode', 'nlink', 'size', 'mtime_ns', 'ctime_ns')
        values = {'st_' + key: i + 100 for i, key in enumerate(fields)}
        values['st_atime_ns'] = 999
        before = types.SimpleNamespace(**values)
        self.assertEqual(list(range(100, 109)), env['metadata'](before))
        atime = dict(values, st_atime_ns=1000)
        self.assertEqual(env['metadata'](before), env['metadata'](types.SimpleNamespace(**atime)))
        for key in fields:
            with self.subTest(key=key):
                changed = dict(values)
                changed['st_' + key] += 1
                self.assertNotEqual(env['metadata'](before), env['metadata'](types.SimpleNamespace(**changed)))


if __name__ == '__main__':
    unittest.main()
