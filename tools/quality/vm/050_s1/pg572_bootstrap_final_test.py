"""Exercise sealed AST constants/functions with independent manager fixture, no VM."""
import ast
import pathlib
import unittest
from pg572_bootstrap_final import PAYLOAD


class Test(unittest.TestCase):
    def test_actual_constant_and_function_closure(self):
        parsed = ast.parse(pathlib.Path(__file__).with_name('pg480_backup_refs.py').read_bytes())
        payload = ast.parse(PAYLOAD)
        assignments = {n.targets[0].id: n for n in payload.body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                       and not isinstance(n.value, ast.BinOp)}
        env = {'parsed': parsed, 'ast': ast}
        for name in ('names', 'nodes', 'constants'):
            exec(compile(ast.Module(body=[assignments[name]], type_ignores=[]), '<extraction>', 'exec'), env)
        code = ast.Module(body=env['constants'] + env['nodes'], type_ignores=[])
        def require(value):
            if not value: raise ValueError('fixture refuses')
        namespace = {'require': require}
        exec(compile(code, '<sealed definitions>', 'exec'), namespace)
        calls = []
        def command(args, limit):
            calls.append((args, limit))
            return b'MainPID=0\nJob=\n'
        namespace['command'] = command
        self.assertEqual(namespace['show']('schubert-nk-api.service', {'MainPID', 'Job'}),
                         {'MainPID': '0', 'Job': ''})
        self.assertEqual(calls, [(['/usr/bin/systemctl', 'show', 'schubert-nk-api.service',
                                 '--property=Job,MainPID'], 1048576)])
        with self.assertRaises(ValueError): namespace['show']('foreign.service', {'MainPID', 'Job'})
        with self.assertRaises(ValueError): namespace['show']('schubert-nk-api.service', {'MainPID'})
        fields = namespace['configuration_fields']()
        self.assertIn('ExecStart', fields)
        self.assertIn('ReadWritePaths', fields)
        self.assertEqual(len(namespace['UNITS']), 10)


if __name__ == '__main__': unittest.main()
