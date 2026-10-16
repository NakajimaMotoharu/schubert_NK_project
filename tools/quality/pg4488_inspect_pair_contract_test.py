"""Independent exact identities and rejection vectors, with saved full private input."""
import copy
import hashlib
import json
import unittest
from pg1446_current_cold_stage import W
import pg4488_inspect_pair_contract as contract


class ExactInspectPair(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=W/'pg4486-preserved-inspect-proofs-v1'
        raw=(folder/'second-pair.private.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!='e1558f41bdf20aa2c85eaf7a821820d4d339b9f1dc0a657f1e4c0b9924c5dbaa':raise ValueError('fixed input')
        cls.pair=json.loads(raw);cls.data=json.loads((folder/'second-data.private.json').read_bytes())

    def test_all_full_descriptors_and_literal_identity(self):
        self.assertEqual((827198,16494387), (self.pair['java']['pid'],self.pair['java']['ticks']))
        self.assertEqual(101,len(self.pair['java']['fds']));self.assertEqual(4,len(self.pair['python']['fds']))
        for label in ['java','python']:self.assertTrue(contract.stable(label,self.pair[label],copy.deepcopy(self.pair[label])))
        self.assertTrue(contract.database_socket(self.pair));self.assertTrue(contract.peers(self.data,self.data))

    def test_every_fd_target_metadata_and_fdinfo_is_checked(self):
        for label in ['java','python']:
            for fd in self.pair[label]['fds']:
                for field in ['target','metadata','fdinfo']:
                    v=copy.deepcopy(self.pair[label]);v['fds'][fd][field]=None
                    with self.subTest(label=label,fd=fd,field=field),self.assertRaises(ValueError):contract.stable(label,self.pair[label],v)

    def test_all_authority_identity_and_children_fields_reject(self):
        for label in ['java','python']:
            old=self.pair[label]
            for key in ['pid','ticks','argvSha256','cgroup','children','fds']:
                v=copy.deepcopy(old);v[key]=None
                with self.subTest(label=label,key=key),self.assertRaises(ValueError):contract.stable(label,old,v)
            for key in old['authority']:
                v=copy.deepcopy(old);v['authority'][key]='invalid'
                with self.subTest(label=label,key=key),self.assertRaises(ValueError):contract.stable(label,old,v)

    def test_only_explicit_orphan_transition(self):
        v=copy.deepcopy(self.pair['python']);v['authority']['PPid']='1'
        self.assertTrue(contract.stable('python',self.pair['python'],v,True))
        with self.assertRaises(ValueError):contract.stable('python',self.pair['python'],v)
        v['fds']['4']=v['fds']['3']
        with self.assertRaises(ValueError):contract.stable('python',self.pair['python'],v,True)

    def test_socket_both_endpoints_duplicate_state_and_inode_reject(self):
        for field,old,new in [('tcp6','14177460','99999999'),('tcp','14176496','99999999'),('tcp6','0000000000000000FFFF00000100007F:9AA0','0000000000000000FFFF00000100007F:9AA1')]:
            v=copy.deepcopy(self.pair);v[field]=v[field].replace(old,new)
            with self.subTest(field=field,old=old),self.assertRaises(ValueError):contract.database_socket(v)
        v=copy.deepcopy(self.pair);v['tcp6']+='\n'.join(l for l in v['tcp6'].splitlines()if '14177460'in l)+'\n'
        with self.assertRaises(ValueError):contract.database_socket(v)

    def test_every_data_section_and_management_resource_checked(self):
        for key in self.data:
            v=copy.deepcopy(self.data);v[key]=None
            with self.subTest(key=key),self.assertRaises((ValueError,TypeError)):contract.peers(self.data,v)
        v=copy.deepcopy(self.data);v['database']['peers'][0]['state']='active';self.assertTrue(contract.peers(self.data,v))
        for key in ['address','application','backendStart','pid','port','state','user']:
            v=copy.deepcopy(self.data);v['database']['peers'][0][key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):contract.peers(self.data,v)
        v=copy.deepcopy(self.data);v['database']['peers']=[];v['database']['locks']=[];v['flocks']=[]
        self.assertTrue(contract.peers(self.data,v,True))
        with self.assertRaises(ValueError):contract.peers(self.data,self.data,True)


if __name__=='__main__':unittest.main()
