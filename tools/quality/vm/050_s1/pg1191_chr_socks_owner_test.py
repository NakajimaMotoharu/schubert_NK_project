import ast
import unittest
from pg1191_chr_socks_owner import qualify, EXPECTED
from pg1192_current_resume_a01_v3 import code


class SocksOwnerTest(unittest.TestCase):
    def literal(self):
        return {'pid':401093,'ticks':5513311,'argvSha256':'e0ec1bc2ff2373f4702a2ab31ef7df6da5c164288db178e17f11661c3676bf6a',
                'executable':'/usr/bin/ssh','ppid':4192,'uids':(1000,1000,1000,1000),
                'gids':(1000,1000,1000,1000),'listenerAddresses':('0100007F:D781',)}

    def test_literal_current_owner_and_input_preserved(self):
        value=self.literal();self.assertEqual(qualify(value),self.literal());self.assertEqual(value,self.literal())

    def test_null_unknown_different_owner_foreign_and_nonloopback_rejected(self):
        value=self.literal()
        for bad in [None,{},[],dict(value,unknown=0)]:
            with self.assertRaises(ValueError):qualify(bad)
        for key in value:
            for bad in [None,True,'foreign']:
                with self.subTest(key=key),self.assertRaises(ValueError):qualify(dict(value,**{key:bad}))
        for key,bad in [('pid',401094),('ticks',5513312),('uids',(0,0,0,0)),('gids',(1000,1000,1000,False)),('listenerAddresses',()),('listenerAddresses',('00000000:D781',)),('listenerAddresses',('0100007F:D781','00000000:D781'))]:
            with self.assertRaises(ValueError):qualify(dict(value,**{key:bad}))

    def test_actual_new_only_guard_pre_before_after_no_old_retry(self):
        s=code();ast.parse(s)
        self.assertEqual(s.count('require_owner()'),3)
        self.assertTrue('pg1192-chr-a01-native-v1' in s)
        self.assertFalse('pg1190-chr-a01-native-v1' in s)
        self.assertTrue(s.index('require_owner()')<s.index('before=json.loads('))
        self.assertTrue('cbca8738-3b24-4090-b77c-bf029677cdd6' in s)


if __name__ == '__main__':unittest.main()
