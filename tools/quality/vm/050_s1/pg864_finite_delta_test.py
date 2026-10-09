"""Independent literal publication oracle and preserved old-original counterexamples."""
import copy,hashlib,stat
from pg864_finite_delta import finite_trees,epoch_bytes
E=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=9de2d03c-28c7-4647-97d9-c66ace06048c\ncutoff_utc=2026-10-09T05:42:22.532331Z\nactivation_id=021111b4-6de5-4733-917d-5ac176240ffc\npermit_sha256=-\n'
A=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG862\nmanifest_sha256=20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe\n'
S='/run/schubert-nk/startup';P='/etc/schubert-nk/release-approval'
def record(mode,size,digest):return {'metadata':[1,2,0,0,mode,1,size,8,9],'sha256':digest}
old={S:{S:record(stat.S_IFDIR|0o700,47,None),S+'/epoch.current':record(stat.S_IFREG|0o600,len(E),'old'),S+'/old.permit':record(stat.S_IFREG|0o600,8,'permit')},P:{P:record(stat.S_IFDIR|0o700,4096,None),P+'/current':record(stat.S_IFREG|0o400,len(A),'oldapproval')},'original':{'DONE':record(stat.S_IFREG|0o600,10,'originalDONE')}}
assert epoch_bytes('11111111-2222-4333-8444-555555555555')==E
assert finite_trees(old,copy.deepcopy(old),'before',None)
new=copy.deepcopy(old);new[S][S+'/epoch.current']=record(stat.S_IFREG|0o600,len(E),hashlib.sha256(E).hexdigest());new[S][S+'/epoch.current']['metadata'][1]=77
assert finite_trees(old,new,'epoch',E) and not finite_trees(old,new,'before',E)
new[P][P+'/current']=record(stat.S_IFREG|0o400,len(A),hashlib.sha256(A).hexdigest());new[P][P+'/current']['metadata'][1]=78
for phase in ('approval','after','release'):assert finite_trees(old,new,phase,E)
for name,entry in [(S,S+'/old.permit'),('original','DONE')]:
 x=copy.deepcopy(new);x[name][entry]['sha256']='foreign';assert not finite_trees(old,x,'after',E)
for index in (0,2,3,4,5,6):
 x=copy.deepcopy(new);x[S][S+'/epoch.current']['metadata'][index]+=1;assert not finite_trees(old,x,'after',E)
for bad in (None,b'',E.replace(b'INVALID',b'ISSUED'),E.replace(b'11111111-2222-4333-8444-555555555555',b'8b153538-1523-4987-a456-6cbea0d345ee'),E.replace(b'cc9ed874',b'aa9ed874'),E+b'x'):
 assert not finite_trees(old,new,'after',bad)
for phase in (None,'unknown'):
 assert not finite_trees(old,new,phase,E)
x=copy.deepcopy(new);x[S]['new.permit']=record(stat.S_IFREG|0o600,1,'x');assert not finite_trees(old,x,'after',E)
print('DEP864001 independent finite phase delta/null/foreign/old original/security/new permit PASS; mutation0')
