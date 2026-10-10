"""Literal distinct old/new payloads; strict manifest and metadata negatives."""
import copy
import hashlib
import json
import unittest
from pg1123_dual_source_artifacts import qualify


class DualSourceTest(unittest.TestCase):
    def fixture(self):
        old_data={'VERSION':b'old\n','api/api.jar':b'old-main'}
        new_data={'VERSION':b'new\n','api/api.jar':b'new-main'}
        old={k:hashlib.sha256(v).hexdigest()for k,v in old_data.items()}
        bom=dict(source={'commit':'d'*40},artifacts=[
            dict(path='VERSION',size=4,sha256=hashlib.sha256(b'new\n').hexdigest()),
            dict(path='api/api.jar',size=8,sha256=hashlib.sha256(b'new-main').hexdigest())])
        manifest=json.dumps(bom).encode();digest=hashlib.sha256(manifest).hexdigest()
        now={k:dict(metadata=[1,2,0,0,0,1,1,1,1],sha256=None)
             for k in ['', 'api','VERSION','api/api.jar','RELEASE-MANIFEST.json','SHA256SUMS']}
        now['RELEASE-MANIFEST.json']['sha256']=digest
        before={k:dict(**copy.deepcopy(v),acl={},target=None)for k,v in now.items()}
        args=[old,before,now,manifest,old_data.__getitem__,new_data.__getitem__,'d'*40,digest,2]
        return args,old_data,new_data,bom

    def test_literal_distinct_sources_not_current_against_old_hash(self):
        args,_,new,_=self.fixture();result=qualify(*args)
        self.assertTrue(result['sourceScopesSeparated']);self.assertEqual(result['currentArtifactsVerified'],2)
        self.assertFalse(result['formalAccepted'])
        args[4]=new.__getitem__
        with self.assertRaises(ValueError):qualify(*args)

    def test_manifest_source_digest_paths_sizes_and_hashes(self):
        args,_,_,_=self.fixture();args[6]='a'*40
        with self.assertRaises(ValueError):qualify(*args)
        args,_,_,_=self.fixture();args[7]='0'*64
        with self.assertRaises(ValueError):qualify(*args)
        for key,bad in [('path','../foreign'),('path','/absolute'),('size',True),
                        ('size',99),('sha256','0'*64)]:
            args,_,_,bom=self.fixture();bom['artifacts'][0][key]=bad
            args[3]=json.dumps(bom).encode();args[7]=hashlib.sha256(args[3]).hexdigest()
            with self.assertRaises(ValueError):qualify(*args)

    def test_closure_metadata_link_acl_missing_extra_and_null(self):
        args,_,_,_=self.fixture();args[2]['extra']={}
        with self.assertRaises(ValueError):qualify(*args)
        for key,bad in [('metadata',[]),('sha256','wrong')]:
            args,_,_,_=self.fixture();args[2]['api/api.jar'][key]=bad
            with self.assertRaises(ValueError):qualify(*args)
        for key,bad in [('acl',{'foreign':'00'}),('target','other')]:
            args,_,_,_=self.fixture();args[1]['api/api.jar'][key]=bad
            with self.assertRaises(ValueError):qualify(*args)
        for index in [0,1,2,3]:
            args,_,_,_=self.fixture();args[index]=None
            with self.assertRaises(ValueError):qualify(*args)


if __name__=='__main__':unittest.main()
