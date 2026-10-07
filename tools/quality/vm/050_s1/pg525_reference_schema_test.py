"""Independent literal PG502 schema/malformed vectors. No VM authority."""
import copy
from pg525_prestop_owned_handoff_v1 import cold_lock_reference
value={'units':{str(x):{} for x in range(10)},'rows':{str(x):[] for x in range(24)},'trees':{},'owner':[2200,123456,{'maintenance.lock':[28,20,0,0,33152,1,0,100,100],'startup-admission.lock':[28,21,0,0,33152,1,0,100,100]}],'prepared':True}
count=0
def check(v,expected):
 global count
 assert cold_lock_reference(v) is expected;count+=1
check(value,True);check(None,False);check({},False)
for k in value:
 v=copy.deepcopy(value);del v[k];check(v,False)
 v=copy.deepcopy(value);v[k]=None;check(v,False)
v=copy.deepcopy(value);v['current']='runtime-artifact';check(v,False)
for v in [[],[1,2,{}],[True,2,value['owner'][2]],[2,True,value['owner'][2]],[2,1,{}],[2,1,[]],[2,1,value['owner'][2],None]]:
 bad=copy.deepcopy(value);bad['owner']=v;check(bad,False)
for name in value['owner'][2]:
 for i in range(9):
  bad=copy.deepcopy(value);bad['owner'][2][name][i]=None;check(bad,False)
  bad=copy.deepcopy(value);bad['owner'][2][name][i]=True;check(bad,False)
 for i,field in enumerate([28,0,1,1,33188,2,1,100,100]):
  if i in [0,7,8]:continue
  bad=copy.deepcopy(value);bad['owner'][2][name][i]=field;check(bad,False)
 bad=copy.deepcopy(value);bad['owner'][2][name]=bad['owner'][2][name][:-1];check(bad,False)
 bad=copy.deepcopy(value);del bad['owner'][2][name];check(bad,False)
print('PG525_SCHEMA_ORACLE independentAssertions='+str(count)+' distinctArtifactSchema=true vmActions0=true productionPT0=true')
