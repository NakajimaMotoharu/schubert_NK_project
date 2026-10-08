"""Pure capture/same-peer/owned-FD protocol negatives. No Root/VM actions."""
import ast
from pathlib import Path
import unittest
from pg647_retirement_contract import require
from pg647_build import java_source

R = Path(__file__).parent


def functions():
    tree = ast.parse((R/'pg647_runtime_retirement_refs.py').read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('capture_definition','peer_socket')]
    env = {'ast': ast, 'require': require}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pure new retirement protocol>', 'exec'), env)
    return env


class Protocol(unittest.TestCase):
    def test_full_capture_adaptation_and_own_lock_only(self):
        source = ast.parse((R/'pg646_completed_baseline.py').read_text())
        raw = ast.literal_eval(next(n.value for n in source.body if isinstance(n, ast.Assign)
                                   and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets)))
        value = functions()['capture_definition'](raw); compile(value, '<adapted current snapshot>', 'exec')
        for text in ('owner();directories();connection()', "['FLOCK','ADVISORY','WRITE',str(held[0])]",
                     '18 if removed else 19', 'None if removed else', 'len(v)==19', 'live else', '504'):
            self.assertIn(text, value)
        with self.assertRaises(ValueError): functions()['capture_definition'](raw.replace("len(set(paths))==19", 'True'))

    def test_same_backend_peer_owned_established_socket(self):
        method = functions()['peer_socket']
        row = ['0:', '0100007F:9C40', '0100007F:1538', '01', '0', '0', '0', '0', '0', '42']
        self.assertTrue(method([row], {'42'}, 40000))
        ipv6 = list(row); ipv6[1] = '0000000000000000FFFF00000100007F:9C40'; ipv6[2] = '0000000000000000FFFF00000100007F:1538'
        self.assertTrue(method([ipv6], {'42'}, 40000))
        for which in ('source','target','state','inode','duplicate','absent'):
            changed = list(row)
            if which == 'source': changed[1] = '0100007F:9C41'
            if which == 'target': changed[2] = '0100007F:1539'
            if which == 'state': changed[3] = '0A'
            if which == 'inode': changed[9] = 'foreign'
            rows = [changed, changed] if which == 'duplicate' else [] if which == 'absent' else [changed]
            with self.subTest(which=which), self.assertRaises(ValueError): method(rows, {'42'}, 40000)
        for port in (None, True, 0, 65536):
            with self.subTest(port=port), self.assertRaises(ValueError): method([row], {'42'}, port)

    def test_java_current_original_and_immutable_target_bindings(self):
        value = java_source()
        for item in ('Pg647RuntimeRetirement', 'Pg642NativeStop.verifyOriginal()', 'pg647_runtime_retirement_refs.py',
                     'PG647-runtime-retirement', 'onceResumeRetired=true', 'originalCompletedUnchanged=true',
                     'MaintenanceFileLock.create().tryExclusive', 'StartupAdmissionFile.create().tryExclusive',
                     'db', 'database.rollback();database.close()', 'held.release()'):
            self.assertIn(item, value)
        self.assertNotIn('Pg633PendingDeployment.original()', value)
        self.assertNotIn('pg635_resume_refs', value)


if __name__ == '__main__': unittest.main()
