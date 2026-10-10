"""Independent approved literal roles/modes; old six-role false readiness counterexample."""
import copy
import unittest
from pg1119_cold_native_contract import plan


class NativeTest(unittest.TestCase):
    def fixture(self):
        parent=dict(kind='directory',uid=0,gid=0,mode=0o711,acl=[])
        accounts={'schubert-backup':(1101,1101),'schubert-inspector':(1102,1102),
                  'schubert-api':(1103,1103),'schubert-web':(1104,1104)}
        entries={x:dict(kind='directory',uid=0,gid=0,mode=0o700,acl=[])
                 for x in ['parent','cleanup','expiry','root-api']}
        entries['backup']=dict(kind='directory',uid=1101,gid=1101,mode=0o700,acl=[])
        entries['inspector']=dict(kind='directory',uid=1102,gid=1102,mode=0o700,acl=[])
        rw={'morning':{'parent'},'api':{'root-api193','ordinary-api193'},
            'web':{'root-web193','ordinary-web193'},'backup':{'backup'},
            'cleanup':{'cleanup'},'expiry':set(),'inspector':set()}
        return parent,entries,rw,accounts

    def test_old_six_require_four_new_roles_and_parent_read(self):
        args=self.fixture();value=plan(*args)
        self.assertEqual(value['parentModeChange'],(0o711,0o755))
        self.assertEqual(value['newOnlyDirectories'],[
            dict(role='ordinary-api193',uid=1103,gid=1103,mode=0o700),
            dict(role='ordinary-web193',uid=1104,gid=1104,mode=0o700),
            dict(role='root-api193',uid=0,gid=0,mode=0o700),
            dict(role='root-web193',uid=0,gid=0,mode=0o700)])
        self.assertFalse(value['nativeAccepted'])
        self.assertTrue(value['requiresOwnedTerminalScope'])
        self.assertEqual(args,self.fixture())

    def test_complete_and_partly_existing_roles(self):
        parent,entries,rw,accounts=self.fixture();parent['mode']=0o755
        entries['root-api193']=dict(kind='directory',uid=0,gid=0,mode=0o700,acl=[])
        self.assertEqual(len(plan(parent,entries,rw,accounts)['newOnlyDirectories']),3)
        for role,uid in [('root-web193',0),('ordinary-api193',1103),('ordinary-web193',1104)]:
            entries[role]=dict(kind='directory',uid=uid,gid=uid,mode=0o700,acl=[])
        value=plan(parent,entries,rw,accounts)
        self.assertIsNone(value['parentModeChange']);self.assertEqual(value['newOnlyDirectories'],[])

    def test_null_missing_unknown_schema(self):
        args=list(self.fixture())
        for index in range(4):
            for bad in [None,{},[],dict(unknown=0)]:
                values=copy.deepcopy(args);values[index]=bad
                with self.subTest(index=index,bad=bad),self.assertRaises(ValueError):plan(*values)

    def test_wrong_owner_mode_type_acl_preserved_roles(self):
        for role in ['parent','cleanup','expiry','root-api','backup','inspector']:
            for key,bad in [('kind','symlink'),('uid',True),('uid',9999),('gid',9999),
                            ('mode',True),('mode',0o755),('acl',['foreign'])]:
                args=list(self.fixture());args[1][role][key]=bad
                with self.subTest(role=role,key=key),self.assertRaises(ValueError):plan(*args)
        for mode in [True,0o700,0o777,None]:
            args=list(self.fixture());args[0]['mode']=mode
            with self.assertRaises(ValueError):plan(*args)
        for key in ['uid','gid']:
            args=list(self.fixture());args[0][key]=False
            with self.assertRaises(ValueError):plan(*args)

    def test_declaration_account_and_inventory_drift(self):
        for role in ['morning','api','web','backup','cleanup','expiry','inspector']:
            for bad in [None,[],{'root-api'},set(),{'unknown'}]:
                args=list(self.fixture());args[2][role]=bad
                if bad==self.fixture()[2][role]:continue
                with self.subTest(role=role),self.assertRaises(ValueError):plan(*args)
        for bad in [(0,0),(True,1103),(1103,),[1103,1103],None]:
            args=list(self.fixture());args[3]['schubert-api']=bad
            with self.assertRaises(ValueError):plan(*args)
        args=list(self.fixture());args[1]['unknown']={}
        with self.assertRaises(ValueError):plan(*args)


if __name__=='__main__':unittest.main()
