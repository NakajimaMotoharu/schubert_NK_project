import copy
import hashlib
import unittest
import pg4122_fixed_terminal_native_contract as subject


class NativeContractTest(unittest.TestCase):
    INV='1234567890abcdef1234567890abcdef'

    def argv(self,label='API',inv=INV):
        return [b'/opt/jdk-25.0.4/bin/java',('-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid='+label+'-'+inv+'-ordinary').encode(),b'main',b'']

    def test_ss_literal_closed_roles_and_option_not_vendor_writer(self):
        for unit,label,directory in [('schubert-nk-api.service','API','ordinary-api193'),('schubert-nk-web.service','WEB','ordinary-web193')]:
            self.assertEqual('/run/schubert-nk/pt-coverage/'+directory+'/'+self.INV+'.terminal.exec',subject.destination(unit,self.INV,self.argv(label)))
        for value in [b'output=file',b'append=true',b'dumponexit=true',b'sessionid=WEB-'+self.INV.encode()+b'-ordinary',b'destfile=/tmp/foreign']:
            bad=self.argv();bad[1]=bad[1].replace(b'output=none',value)
            with self.assertRaises(ValueError):subject.destination('schubert-nk-api.service',self.INV,bad)
        for unit,inv,args in [(None,self.INV,self.argv()),('caddy.service',self.INV,self.argv()),('schubert-nk-api.service','0'*32,self.argv()),('schubert-nk-api.service',self.INV,[*self.argv(),self.argv()[1]]),('schubert-nk-api.service',self.INV,None)]:
            with self.assertRaises(ValueError):subject.destination(unit,inv,args)

    def fixture(self):
        exports={u:subject.destination(u,self.INV,self.argv(label))for u,(label,d)in subject.ROLES.items()}
        dirs={p.rsplit('/',1)[0]for p in exports.values()}
        before={p:{'metadata':[1,2+i,9,10,0o40700,2,4096,20,21],'sha256':None}for i,p in enumerate(sorted(dirs))}
        before['/old.exec']={'metadata':[1,8,9,10,0o100600,1,9,20,21],'sha256':'f'*64}
        identities={u:{'uid':9,'gid':10}for u in exports}
        value=bytes([1,192,192,16,7,99]);after=copy.deepcopy(before)
        for i,p in enumerate(exports.values()):after[p]={'metadata':[1,30+i,9,10,0o100600,1,len(value),22,23],'sha256':hashlib.sha256(value).hexdigest()}
        return before,after,exports,identities,value

    def test_only_exact_two_new_streams_no_prior_mutation_or_crc_claim(self):
        b,a,e,ids,value=self.fixture()
        self.assertTrue(subject.preserved(b,b,e,set(),ids,lambda p:value,lambda p:[]))
        for count in [1,2]:
            finished=set(list(e)[:count]);subset={k:v for k,v in a.items()if k in b or k in {e[u]for u in finished}}
            self.assertTrue(subject.preserved(b,subset,e,finished,ids,lambda p:value,lambda p:[]))

    def test_extra_missing_existing_old_changed_inode_owner_mode_link_hash_header_acl_refused(self):
        b,a,e,ids,value=self.fixture();key=e['schubert-nk-api.service'];done=set(e)
        for change in ['extra','missing','old','uid','gid','mode','link','device','hash','header','acl','priorExists','parentInode']:
            bb,aa=copy.deepcopy(b),copy.deepcopy(a);read=lambda p:value;attr=lambda p:[]
            if change=='extra':aa['/foreign']=aa[key]
            elif change=='missing':del aa[key]
            elif change=='old':aa['/old.exec']['sha256']='0'*64
            elif change in ['uid','gid','mode','link','device']:aa[key]['metadata'][{'device':0,'uid':2,'gid':3,'mode':4,'link':5}[change]]+=1
            elif change=='hash':aa[key]['sha256']='0'*64
            elif change=='header':read=lambda p:b'xxxxx!'
            elif change=='acl':attr=lambda p:['system.posix_acl_access']
            elif change=='priorExists':bb[key]=aa[key]
            else:aa[key.rsplit('/',1)[0]]['metadata'][1]+=1
            with self.subTest(change=change),self.assertRaises(ValueError):subject.preserved(bb,aa,e,done,ids,read,attr)


if __name__=='__main__':unittest.main()
