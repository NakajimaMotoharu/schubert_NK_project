import hashlib
import unittest
from pg1263_backup_config_responsibility_v2 import verify_member,TEMPLATES,EFFECTIVE,HOST_ENV

class ReleaseVsHostConfigContractTest(unittest.TestCase):
    def test_actual_eight_names_preservation_and_template_not_runtime_authority(self):
        template=b'independent template input';body=b'independent instantiated host input'
        hashes={p:hashlib.sha256(template).hexdigest()for p in TEMPLATES.values()};hashes.update({p:hashlib.sha256(body).hexdigest()for p in EFFECTIVE.values()})
        for name in set(TEMPLATES)|set(EFFECTIVE)|HOST_ENV:
            mode=0o600 if name in {'api.env','web.env'}else 0o640;identity=(0,986,mode)
            result=verify_member(name,body,body,identity,identity,986,hashes)
            self.assertIn('HOST',result)
            if name in TEMPLATES:self.assertEqual(result,'SIGNED_TEMPLATE_REGISTERED_DEPLOYED_HOST_BYTES_NOT_TEMPLATE_BYTE_AUTHORITY')
            for source,target in [((1,986,mode),identity),(identity,(0,986,0o644)),((0,999,mode),identity)]:
                with self.assertRaises(ValueError):verify_member(name,body,body,source,target,986,hashes)
            with self.assertRaises(ValueError):verify_member(name,body,b'foreign',identity,identity,986,hashes)
            if name not in HOST_ENV:
                path=(EFFECTIVE if name in EFFECTIVE else TEMPLATES)[name]
                for bad in [{},dict(hashes,**{path:'z'*64}),dict(hashes,**{path:None})]:
                    with self.assertRaises(ValueError):verify_member(name,body,body,identity,identity,986,bad)
                if name in EFFECTIVE:
                    with self.assertRaises(ValueError):verify_member(name,body,body,identity,identity,986,dict(hashes,**{path:'f'*64}))
        for name in [None,'../api.yml','runtime/inbox-inspector.env','foreign.yml']:
            with self.assertRaises(ValueError):verify_member(name,body,body,(0,986,0o640),(0,986,0o640),986,hashes)

if __name__=='__main__':unittest.main()
