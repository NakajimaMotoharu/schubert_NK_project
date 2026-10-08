"""Pure capture/same-peer/owned-FD protocol negatives. No Root/VM actions."""
import ast
import stat
from pathlib import Path
from types import SimpleNamespace
import unittest
from pg647_retirement_contract import require
from pg647_build import java_source
from pg647_retirement_native import source

R = Path(__file__).parent


def functions():
    tree = ast.parse((R/'pg647_runtime_retirement_refs.py').read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('capture_definition','peer_socket','directory_identity','directory_witness')]
    env = {'ast': ast, 'require': require, 'stat': stat}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pure new retirement protocol>', 'exec'), env)
    return env


class Protocol(unittest.TestCase):
    def test_transport_current_byte_hash_and_no_old_operation_slots(self):
        value = source(); compile(value, '<fixed new transport>', 'exec')
        for text in ('pg647-retirement-tools-v1','pg647-retirement-stage-v1',"('stage','retire')",
                     'Pg642NativeStop.class','pg646_completed_baseline.py','pg647_runtime_retirement_refs.py',
                     "build['files'].items()", 'pg647-cli-v1.private.log', 'PG647_STAGED'):
            self.assertIn(text, value)
        for text in ('pg635-resume-tools-v1','Pg635ResumePreparation','pg629_failed_receipt.py'):
            self.assertNotIn(text, value)

    def test_runtime_initial_security_and_each_namespace_fd_recheck(self):
        check = functions()['directory_witness']
        base = dict(st_dev=28, st_ino=2576, st_uid=0, st_gid=0,
                    st_mode=stat.S_IFDIR | 0o755, st_nlink=2, st_atime_ns=1)
        original = SimpleNamespace(**base)
        self.assertIsNone(check(original, original, original, [], True))
        for name, values in {'st_uid': (1,), 'st_gid': (1,), 'st_mode': (stat.S_IFDIR|0o700, stat.S_IFDIR|0o777, stat.S_IFREG|0o755), 'st_nlink': (1, 3)}.items():
            for value in values:
                bad = SimpleNamespace(**dict(base, **{name:value}))
                with self.subTest(initial=name, value=value), self.assertRaises(ValueError):
                    check(bad, bad, bad, [], True)
        for name in ('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink'):
            bad = SimpleNamespace(**dict(base, **{name:base[name]+1}))
            for position in range(3):
                inputs = [original, original, original]; inputs[position] = bad
                with self.subTest(drift=name, position=position), self.assertRaises(ValueError):
                    check(*inputs, [], True)
        for acl in ('system.posix_acl_access', 'system.posix_acl_default'):
            with self.subTest(acl=acl), self.assertRaises(ValueError):
                check(original, original, original, [acl], True)
        read = SimpleNamespace(**dict(base, st_atime_ns=2))
        self.assertIsNone(check(read, read, original, [], True))
        private = SimpleNamespace(**dict(base, st_mode=stat.S_IFDIR|0o700))
        self.assertIsNone(check(private, private, private, [], False))

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
