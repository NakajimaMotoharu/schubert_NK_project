"""Independent SS193196 six-role/legacy current namespace delta vectors, no VM authority."""
import copy,pathlib,stat,sys,types
sys.modules.setdefault('dbus',types.SimpleNamespace())
import pg518_native_role_refs as h
n=0
def check(v):
 global n
 if not v:raise AssertionError('native namespace independent oracle')
 n+=1
root='/run/schubert-nk/pt-coverage'
previous={root:{'metadata':[28,1,0,0,stat.S_IFDIR|0o755,11,220,100,100],'sha256':None}}
for role in ['parent','backup','cleanup','expiry','inspector','root-api','root-web','ordinary-api','ordinary-web']:
 previous[root+'/'+role]={'metadata':[28,len(previous)+1,0,0,stat.S_IFDIR|0o700,2,40,100,100],'sha256':None}
previous[root+'/parent/old.exec']={'metadata':[28,20,0,0,stat.S_IFREG|0o600,1,500,100,100],'sha256':'a'*64}
ids={'root-api193':[0,0],'root-web193':[0,0],'ordinary-api193':[999,999],'ordinary-web193':[998,998],'ordinary-inspector196':[997,997],'ordinary-bootstrap196':[999,999]}
actual=copy.deepcopy(previous)
check(h.coverage_delta(actual,previous,ids))
for role in ids:
 actual[root]['metadata'][5]+=1;actual[root]['metadata'][6:]=[300,200,200]
 actual[root+'/'+role]={'metadata':[28,len(actual)+1,*ids[role],stat.S_IFDIR|0o700,2,40,200,200],'sha256':None}
 check(h.coverage_delta(actual,previous,ids))
for path in previous:
 for k in range(9):
  bad=copy.deepcopy(actual);bad[path]['metadata'][k]+=1
  check(h.coverage_delta(bad,previous,ids)==(path==root and k in [6,7,8]))
 bad=copy.deepcopy(actual);bad[path]['sha256']='b'*64;check(not h.coverage_delta(bad,previous,ids))
for role in ids:
 for k,new in [(1,0),(2,1001),(3,1001),(4,stat.S_IFDIR|0o755),(5,3),(5,1),(8,None)]:
  bad=copy.deepcopy(actual);bad[root+'/'+role]['metadata'][k]=new;check(not h.coverage_delta(bad,previous,ids))
 bad=copy.deepcopy(actual);bad[root+'/'+role]['sha256']='b'*64;check(not h.coverage_delta(bad,previous,ids))
 for foreign in [root+'/'+role+'/file',root+'/foreign']:
  bad=copy.deepcopy(actual);bad[foreign]=previous[root];check(not h.coverage_delta(bad,previous,ids))
for v in [None,{},dict(actual,**{root+'/foreign':previous[root]})]:check(not h.coverage_delta(v,previous,ids))
check(set(h.ROLES)==set(ids));check(h.UNIT_ROLES=={'schubert-nk-api.service':{'root-api193','ordinary-api193'},'schubert-nk-web.service':{'root-web193','ordinary-web193'},'schubert-nk-inbox-inspector.service':{'ordinary-inspector196'},'schubert-nk-bootstrap-admin.service':{'ordinary-bootstrap196'}})
print('PG518_NAMESPACE_DELTA_ORACLE independentAssertions='+str(n)+' legacyOldExecPreserved=true missing6Only=true vmActions0=true productionPT0=true')
