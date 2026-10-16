"""Independent nanosecond metadata and complete actual reader/acceptance closure tests."""
import ast
import types
import unittest
from pyflakes.api import check
import pg4260_stable_admission_image as fixed
import pg4252_current_independent_acceptance as accepted


class StableTest(unittest.TestCase):
    def test_atime_is_not_file_identity(self):
        fields=dict(zip('st_dev st_ino st_uid st_gid st_mode st_nlink st_size st_mtime_ns st_ctime_ns'.split(),range(9)))
        a=types.SimpleNamespace(**fields,st_atime_ns=10,st_mtime=0.1,st_ctime=0.2)
        b=types.SimpleNamespace(**fields,st_atime_ns=20,st_mtime=0.1,st_ctime=0.2)
        self.assertNotEqual(a,b);self.assertEqual(fixed.metadata(a),tuple(range(9)));self.assertEqual(fixed.metadata(a),fixed.metadata(b))
        for key in fields:
            with self.subTest(key=key):
                changed=types.SimpleNamespace(**{**vars(a),key:100})
                self.assertNotEqual(fixed.metadata(a),fixed.metadata(changed))

    def test_full_reader_stat_boundaries(self):
        raw=fixed.payload(fixed.live())
        self.assertEqual(check(raw,'<full stable reader>'),0)
        # Once after held-FD pread and once after the final path byte reread.
        self.assertEqual(raw.count('metadata(path.lstat())==metadata(s)'),2)
        self.assertEqual(raw.count('metadata(os.fstat(fd))==metadata(s)'),1)
        self.assertNotIn('path.lstat()==s',raw)
        self.assertIn('os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC',raw)
        self.assertIn('path.read_bytes()==raw',raw)

    def test_all_generated_acceptance_namespaces(self):
        b=fixed.live()
        for name,raw in [('terminal',accepted.terminal_payload(b)),('rows',accepted.rows_payload(b,'7'*64)),('seal',accepted.seal_payload(b,'7'*64))]:
            with self.subTest(name=name):
                self.assertEqual(check(raw,'<'+name+'>'),0);compile(raw,'<'+name+'>','exec')
                for old in ['pg4016-literal-invariant-current-noargs-once-v1','pg4018-literal-invariant-current-live-binding-v1',accepted.previous.SEAL]:self.assertNotIn(old,raw)
                for node in ast.walk(ast.parse(raw)):
                    if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr in {'run','check_output','Popen'}:
                        text=ast.get_source_segment(raw,node)
                        self.assertNotIn("'systemctl','start'",text);self.assertNotIn("'systemctl','stop'",text)
        original=accepted.previous.terminal_payload(b)
        final=accepted.terminal_payload(b)
        for fn in ['_normal_classify','classify']:
            get=lambda r:ast.dump(next(n for n in ast.parse(r).body if isinstance(n,ast.FunctionDef)and n.name==fn))
            self.assertEqual(get(original),get(final))


if __name__=='__main__':unittest.main()
