"""Important metadata/hash/Unit stability; read-atime alone cannot invalidate immutable bytes."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg5700_failed_native_diagnostic as entry


class Stable(unittest.TestCase):
    def test_atime_only_and_each_important_change(self):
        before=dict(device=1,inode=2,uid=0,gid=0,mode=33152,links=1,size=8,mtimeNanos=10,ctimeNanos=20,atimeNanos=5)
        unit={'InvocationID':'fixed','ExecMainStatus':'30'};sha='a'*64
        self.assertTrue(entry.stable(before,{**before,'atimeNanos':30},unit,unit,sha,sha))
        for key in set(before)-{'atimeNanos'}:
            with self.subTest(key=key):self.assertFalse(entry.stable(before,{**before,key:before[key]+1},unit,unit,sha,sha))
        self.assertFalse(entry.stable(before,before,unit,{**unit,'InvocationID':'foreign'},sha,sha))
        self.assertFalse(entry.stable(before,before,unit,unit,sha,'b'*64))
        for value in(None,{},dict(before,uid=False),dict(before,extra=0)):
            self.assertFalse(entry.stable(value,before,unit,unit,sha,sha))

    def test_private_before_after_saved_before_guard_and_failed_run_not_accepted(self):
        raw=entry.GUEST;self.assertEqual(0,check(raw,'<failed original native input>'))
        self.assertLess(raw.index("save('before.private.json'"),raw.index('raw=p.read_bytes()'))
        self.assertLess(raw.index("save('after.private.json'"),raw.index('assert stable('))
        for forbidden in('systemctl start','systemctl stop','jcmd','unlink(','rmtree('):self.assertNotIn(forbidden,raw)
        dumps=[ast.unparse(n.func)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and ast.unparse(n.func).endswith('dump')]
        self.assertEqual(['json.dump'],dumps)
        self.assertIn("unit['ExecMainStatus']=='30'",raw);self.assertIn("'formalAccepted':False",raw)
        self.assertEqual(0,checkPath(entry.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
