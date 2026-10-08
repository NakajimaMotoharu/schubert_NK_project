"""Literal fixture reusable data only, subject is independently implemented post."""
import unittest
from pg635_resume_contract_test import pair,EXPECTED
from pg636_resume_post_contract import prepared


class Post(unittest.TestCase):
    def test_expected_and_all_protected(self):
        b,a=pair();self.assertTrue(prepared(b,a,EXPECTED))
        for k in b.keys()-{'configuration','runtime','unitFiles','caddyPre'}:
            b,a=pair();a[k]={'foreign':1}
            with self.subTest(k=k),self.assertRaises(ValueError):prepared(b,a,EXPECTED)
        for raw in (None,b'',EXPECTED+b'User=foreign\n',EXPECTED.replace(b'--resume e492',b'--resume f492')):
            b,a=pair()
            with self.assertRaises(ValueError):prepared(b,a,raw)

    def test_runtime_file_and_decl_null_partial(self):
        for mode in ('inode-type','byte','old-file','argv','extra','null'):
            b,a=pair()
            if mode=='inode-type':a['runtime']['metadata'][2]=True
            elif mode=='byte':a['runtime']['sha256']='0'*64
            elif mode=='old-file':a['unitFiles']['/etc/sealed']['sha256']='changed'
            elif mode=='argv':a['configuration']['schubert-nk-morning-controller.service']['ExecStart']='foreign'
            elif mode=='extra':a['configuration']['caddy.service']['User']='root'
            else:a['caddyPre']=None
            with self.subTest(mode=mode),self.assertRaises(ValueError):prepared(b,a,EXPECTED)
        b,a=pair();a['unitFiles'].pop('/etc/sealed')
        with self.assertRaises(ValueError):prepared(b,a,EXPECTED)


if __name__=='__main__':unittest.main()
