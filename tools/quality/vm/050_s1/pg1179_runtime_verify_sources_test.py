import ast
import copy
from pathlib import Path
import types
import unittest
from pg1179_runtime_verify_sources import files, BASE, HASH


class VerifyRuntimeTest(unittest.TestCase):
    def test_generated_readonly_runtime_and_current_binding(self):
        values = files();s = values['pg1179_runtime_refs.py'];ast.parse(s)
        for part in [BASE, HASH, 'CANONICAL_RUNTIME_VERIFICATION']:
            self.assertTrue(part in '\n'.join(values.values()), part)
        for forbidden in ['runtime.owned_prepare(', 'daemon-reload', "action=='prepare'"]:
            self.assertFalse(forbidden in s, forbidden)
        self.assertTrue('refs.check("verify")' in values['Pg1179RuntimeVerify.java'])

    def test_actual_generated_configuration_normal_foreign_null(self):
        s = files()['pg1179_runtime_refs.py'];tree = ast.parse(s)
        nodes = [n for n in tree.body if isinstance(n, ast.Import) and any(a.name == 're' for a in n.names) or isinstance(n, ast.FunctionDef) and n.name in {'require', 'exec_record', 'require_runtime_configuration'}]
        unit = 'schubert-nk-morning-controller.service';directory = Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
        def decl(argv):return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        literal = {unit: {'ExecStart': decl('/usr/bin/java literal-agent --resume 343a5a1b-d064-47d5-88c2-31c36d7ba7a4'), 'DropInPaths': '/etc/pg477-native.conf '+str(directory/'zz-pg1160-once-resume.conf'), 'Other': 'fixed'}}
        env = {'baseline': {'configuration': copy.deepcopy(literal)}, 'MORNING': unit, 'RUNTIME': directory, 'runtime': types.SimpleNamespace(RUN_ID='343a5a1b-d064-47d5-88c2-31c36d7ba7a4', NAME='zz-pg1160-once-resume.conf')}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual readonly runtime contract>', 'exec'), env)
        env['require_runtime_configuration'](literal)
        for key, value in [('ExecStart', None), ('ExecStart', decl('/usr/bin/java literal-agent')), ('DropInPaths', 'foreign'), ('Other', 'changed')]:
            bad = copy.deepcopy(literal);bad[unit][key] = value
            with self.assertRaises(ValueError):env['require_runtime_configuration'](bad)
        for bad in [None, {}, {**literal, 'foreign': {}}]:
            with self.assertRaises(ValueError):env['require_runtime_configuration'](bad)


if __name__ == '__main__':unittest.main()
