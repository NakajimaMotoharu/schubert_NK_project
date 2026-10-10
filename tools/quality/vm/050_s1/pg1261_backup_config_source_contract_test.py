import hashlib
import unittest
from pg1261_backup_config_source_contract import verify_member,SIGNED,HOST

class ExplicitBackupConfigBindingTest(unittest.TestCase):
    def test_all_eight_responsibilities_and_foreign_or_unknown_input(self):
        body=b'independent fixed byte input';hashes={p:hashlib.sha256(body).hexdigest()for p in SIGNED.values()}
        for name in set(SIGNED)|HOST:
            mode=0o600 if name in {'api.env','web.env'}else 0o640;identity=(0,986,mode)
            result=verify_member(name,body,body,identity,identity,986,hashes)
            self.assertEqual(result,'SIGNED_PAYLOAD_AND_FIXED_HOST_SOURCE'if name in SIGNED else'EXTERNAL_HOST_ENV_FIXED_INODE_BYTES_NOT_SIGNED_PAYLOAD')
            for src,tar in [((1,986,mode),identity),(identity,(0,986,0o644)),((0,999,mode),identity)]:
                with self.assertRaises(ValueError):verify_member(name,body,body,src,tar,986,hashes)
            with self.assertRaises(ValueError):verify_member(name,body,b'foreign',identity,identity,986,hashes)
            if name in SIGNED:
                wrong_path=('config/templates/'if name=='backup-profile.json'else'config/effective/')+name
                for bad in [{},{wrong_path:hashlib.sha256(body).hexdigest()},dict(hashes,**{SIGNED[name]:'f'*64})]:
                    with self.assertRaises(ValueError):verify_member(name,body,body,identity,identity,986,bad)
        for name in [None,'../api.yml','runtime/inbox-inspector.env','foreign.yml']:
            with self.assertRaises(ValueError):verify_member(name,body,body,(0,986,0o640),(0,986,0o640),986,hashes)

if __name__=='__main__':unittest.main()
