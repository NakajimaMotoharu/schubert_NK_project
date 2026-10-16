import ast
import hashlib
import stat
import types
import unittest
from pg4094_failed_done_nine_attribute_inspection import payload


class MetadataTest(unittest.TestCase):
    def subject(self, changed=None, content=b'fixed fixture', acl=None):
        raw = payload(); tree = ast.parse(raw)
        metadata = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'metadata')
        loop = next(n for n in tree.body if isinstance(n, ast.For) and isinstance(n.target, ast.Tuple)
                    and [x.id for x in n.target.elts] == ['name', 'digest'])
        values = {'st_dev': 1, 'st_ino': 2, 'st_uid': 0, 'st_gid': 0, 'st_mode': stat.S_IFREG | 0o400,
                  'st_nlink': 1, 'st_size': 13, 'st_mtime_ns': 20, 'st_ctime_ns': 30, 'st_atime_ns': 10}
        class Fixture:
            def __truediv__(self, name): return self
            def lstat(self): return types.SimpleNamespace(**values)
            def read_bytes(self):
                values['st_atime_ns'] = 999
                if changed is not None: values[changed] += 1
                return content
        def require(v):
            if not v: raise ValueError('fixture refused')
        ns = {'stat': stat, 'hashlib': hashlib, 'require': require, 'frozen': Fixture(),
              'os': types.SimpleNamespace(listxattr=lambda p: [] if acl is None else acl),
              'INPUT_HASHES': {'fixture': hashlib.sha256(b'fixed fixture').hexdigest()}}
        exec(compile(ast.Module(body=[metadata, loop], type_ignores=[]), '<actual emitted guard>', 'exec'), ns)
        return values

    def test_atime_update_is_not_identity_drift(self):
        self.assertEqual(999, self.subject()['st_atime_ns'])

    def test_each_nine_attribute_byte_and_acl_drift_refused(self):
        for key in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']:
            with self.subTest(field=key), self.assertRaises(ValueError): self.subject(changed=key)
        with self.assertRaises(ValueError): self.subject(content=b'foreign bytes')
        with self.assertRaises(ValueError): self.subject(acl=['system.posix_acl_access'])

    def test_new_slot_only_inspect_and_no_recompile(self):
        raw = payload()
        self.assertTrue('pg4094-failed-done-owned-inspect-v1' in raw)
        self.assertFalse('pg4090-failed-done-owned-inspect-v1' in raw)
        self.assertTrue("RootFailedDoneRecovery','inspect']" in raw)
        self.assertFalse('subprocess.run(args,env=env' in raw)


if __name__ == '__main__': unittest.main()
