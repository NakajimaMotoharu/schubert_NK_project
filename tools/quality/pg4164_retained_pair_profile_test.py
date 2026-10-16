import copy
import stat
import unittest
import pg4164_retained_pair_profile as p


class PairProfileTest(unittest.TestCase):
    def actor(self,pid):
        java=pid==790010;fds={}
        for key in sorted(p.JVM_FDS if java else p.PY_FDS,key=int):
            n=int(key);mode=stat.S_IFREG|0o640;target=''
            if java:
                if n in [0,1]:target='pipe:[1]';mode=stat.S_IFIFO|0o600
                elif n==2:target='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover/java-stderr.private.log';mode=stat.S_IFREG|0o600
                elif n==3:target='/opt/jdk-25.0.4/lib/modules'
                elif n==4:target=p.ROOT+'/operations/batch.jar'
                elif 5<=n<=45:target=p.ROOT+'/operations/lib/fixture'+key+'.jar'
                elif 46<=n<=83:target=p.ROOT+'/api/lib/fixture'+key+'.jar'
                elif n==84:target='/var/lib/pgpt-s1-preservation/pg4112-canonical-epoch-owned-tools-v1/spotbugs-annotations-4.10.4.jar';mode=stat.S_IFREG|0o400
                elif n in [85,86,88,89]:target='/run'if n in[86,89]else'/run/schubert-nk';mode=stat.S_IFDIR|0o755
                elif n in[87,90,91,100,128]:target='/run/schubert-nk/'+('startup-admission.lock'if n in[100,128]else'maintenance.lock');mode=stat.S_IFREG|0o600
                elif n in[92,93]:target='socket:[1]';mode=stat.S_IFSOCK|0o777
                else:target='/dev/random'if n==94 else'/dev/urandom';mode=stat.S_IFCHR|0o666
            elif n in[0,1,2,6,7]:target='pipe:[1]';mode=stat.S_IFIFO|0o600
            elif n==3:target='socket:[2]';mode=stat.S_IFSOCK|0o777
            else:target='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover/java-stderr.private.log';mode=stat.S_IFREG|0o600
            fds[key]={'target':target,'metadata':[1,n+1,0,0,mode,1,0,20,21],'fdinfo':'pos:\t0\nflags:\t0100000\nmnt_id:\t1\nino:\t1\n'}
        return {'pid':pid,'ticks':14181503 if java else 14180650,'argvSha256':'ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2'if java else'c8c952de1cf05574e3fdcf5effc076e4aac73748367f49aac23f6cb6300e9fb6',
          'authority':{'PPid':'789928'if java else'789926','Uid':'0 0 0 0','Gid':'0 0 0 0','Groups':'0','NoNewPrivs':'0','CapInh':'0000000000000000','CapAmb':'0000000000000000','CapPrm':'000001ffffffffff','CapEff':'000001ffffffffff','CapBnd':'000001ffffffffff'},
          'cgroup':'0::/user.slice/user-1000.slice/session-921.scope\n','children':[]if java else[790010],'fds':fds}

    def test_exact_pair_and_only_confirmed_child_reap_difference(self):
        for pid in [790010,789928]:
            old=self.actor(pid);self.assertTrue(p.stable(old,copy.deepcopy(old),100))
        old=self.actor(789928);new=copy.deepcopy(old);new['children']=[]
        with self.assertRaises(ValueError):p.stable(old,new,100)
        self.assertTrue(p.stable(old,new,100,True))

    def test_every_descriptor_field_and_authority_change_refused(self):
        for pid in [790010,789928]:
            old=self.actor(pid)
            for key in old['fds']:
                for field,value in [('target','/foreign'),('fdinfo','flags:\t01\n'),('metadata',None)]:
                    new=copy.deepcopy(old);new['fds'][key][field]=value
                    with self.subTest(pid=pid,fd=key,field=field),self.assertRaises(ValueError):p.stable(old,new,100)
            for field in old['authority']:
                new=copy.deepcopy(old);new['authority'][field]='foreign'
                with self.assertRaises(ValueError):p.stable(old,new,100)
            for field,value in [('pid',1),('ticks',1),('argvSha256','0'*64),('cgroup','foreign'),('children',[1])]:
                new=copy.deepcopy(old);new[field]=value
                with self.assertRaises(ValueError):p.stable(old,new,100)

    def test_shared_run_chrono_only_bounded_not_owner_inode_mode(self):
        old=self.actor(790010);new=copy.deepcopy(old)
        new['fds']['86']['metadata'][7:]=[40,41]
        self.assertTrue(p.stable(old,new,100))
        with self.assertRaises(ValueError):p.stable(old,new,30)
        new['fds']['86']['metadata'][1]+=1
        with self.assertRaises(ValueError):p.stable(old,new,100)
        with self.assertRaises(ValueError):p.stable(None,new,100)


if __name__=='__main__':unittest.main()
