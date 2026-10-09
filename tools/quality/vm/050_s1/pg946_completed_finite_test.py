"""Independent literal finite publication and genuine-parent refusal fixtures; no VM."""
import ast,copy,datetime,hashlib,stat,unittest
from pg942_completed_sources import refs
from pg944_parent_receipt import completed
E=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=93cb976e-c36c-47a3-b9e2-0ad28d2996de\ncutoff_utc=2026-10-09T19:07:23.894279Z\nactivation_id=0dfe0b7f-0e36-4b81-9086-500d896d1187\npermit_sha256=-\n'
A=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256=b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524\n'
S='/run/schubert-nk/startup';P='/etc/schubert-nk/release-approval'
def methods():
    tree=ast.parse(refs());names={'STARTUP','APPROVAL','OLD_EPOCH','NEW_APPROVAL'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('finite_trees','epoch_bytes')or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in names for t in n.targets)]
    env={};exec('import hashlib,stat,uuid',env);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<finite data functions only>','exec'),env);return env
def record(mode,size,digest):return{'metadata':[1,2,0,0,mode,1,size,8,9],'sha256':digest}
class Test(unittest.TestCase):
    def test_independent_finite_bytes_and_immutable_every_other_entry(self):
        m=methods();finite=m['finite_trees'];self.assertEqual(E,m['epoch_bytes']('11111111-2222-4333-8444-555555555555'))
        old={S:{S:record(stat.S_IFDIR|0o700,4096,None),S+'/epoch.current':record(stat.S_IFREG|0o600,len(E),'old'),S+'/old.permit':record(stat.S_IFREG|0o600,8,'permit')},P:{P:record(stat.S_IFDIR|0o700,4096,None),P+'/current':record(stat.S_IFREG|0o400,len(A),'oldapproval')},'original':{'DONE':record(stat.S_IFREG|0o600,10,'originalDONE')},'native':{'terminal':record(stat.S_IFREG|0o600,10,'native')},'backup':{'archive':record(stat.S_IFREG|0o600,10,'backup')}}
        self.assertTrue(finite(old,copy.deepcopy(old),'before',None))
        new=copy.deepcopy(old);new[S][S+'/epoch.current']=record(stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest());new[S][S+'/epoch.current']['metadata'][1]=77
        self.assertTrue(finite(old,new,'epoch',E));self.assertFalse(finite(old,new,'before',E))
        new[P][P+'/current']=record(stat.S_IFREG|0o400,len(A),hashlib.sha256(A).hexdigest());new[P][P+'/current']['metadata'][1]=78
        for phase in ('approval','after','release'):self.assertTrue(finite(old,new,phase,E))
        for root,name in ((S,S+'/old.permit'),('original','DONE'),('native','terminal'),('backup','archive')):
            wrong=copy.deepcopy(new);wrong[root][name]['sha256']='foreign';self.assertFalse(finite(old,wrong,'after',E))
        for index in (0,2,3,4,5,6):
            wrong=copy.deepcopy(new);wrong[S][S+'/epoch.current']['metadata'][index]+=1;self.assertFalse(finite(old,wrong,'after',E))
        for bad in (None,b'',E.replace(b'INVALID',b'ISSUED'),E.replace(b'11111111-2222-4333-8444-555555555555',b'22ba4479-64b2-4a3c-b2f9-ba720045e821'),E.replace(b'cc9ed874',b'aa9ed874'),E+b'x'):
            self.assertFalse(finite(old,new,'after',bad))
        for phase in (None,'unknown'):self.assertFalse(finite(old,new,phase,E))
        wrong=copy.deepcopy(new);wrong[S]['new.permit']=record(stat.S_IFREG|0o600,1,'x');self.assertFalse(finite(old,wrong,'after',E))
    def test_literal_pid1_and_done_old_unknown_ready_are_not_genuine(self):
        common={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'75f48ce36cd740e98a801eede7fdbb7f','__MONOTONIC_TIMESTAMP':'186742282251'}
        rows=[{**common,'__CURSOR':'literal-job','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'195974','JOB_TYPE':'start','JOB_RESULT':'done','__REALTIME_TIMESTAMP':str(int(datetime.datetime.fromisoformat('2026-10-09T19:31:24+00:00').timestamp())*1000000)},{**common,'__CURSOR':'literal-success','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]
        done=b'NKDONE1\n93cb976e-c36c-47a3-b9e2-0ad28d2996de\n2026-10-09T19:07:23.894279Z\n0dfe0b7f-0e36-4b81-9086-500d896d1187\n2026-10-09T19:31:23.759513Z\n0\n'
        self.assertEqual(1200,completed(rows,done)['elapsedSeconds'])
        for key,value in (('_PID','2'),('_UID','1'),('_BOOT_ID','a'*32),('INVOCATION_ID','b'*32),('__MONOTONIC_TIMESTAMP','187342282252'),('JOB_RESULT','failed'),('JOB_ID','195975'),('MESSAGE_ID','ready')):
            bad=copy.deepcopy(rows);bad[0][key]=value
            with self.assertRaises(ValueError):completed(bad,done)
        for bad in ([],rows[:1],rows+[copy.deepcopy(rows[0])]):
            with self.assertRaises(ValueError):completed(bad,done)
        for bad in (done.replace(b'\n0\n',b'\n10\n'),done.replace(b'93cb976e',b'83cb976e'),done.replace(b'19:31:23',b'19:35:23'),done[:-1]):
            with self.assertRaises(ValueError):completed(rows,bad)
if __name__=='__main__':unittest.main()
