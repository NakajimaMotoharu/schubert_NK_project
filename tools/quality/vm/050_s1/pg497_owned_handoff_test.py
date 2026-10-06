"""Independent literal ownership/idle-expiry admission vectors, runtime actions0."""
import ast,pathlib,re,types
import pg497_owned_handoff as h
import pg481_native_owned_stop as w
definitions=[n for n in ast.parse((pathlib.Path(__file__).parent/'pg477_unit_references.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record']
scope={'re':re};exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pure parser>','exec'),scope)
h.exec_record=scope['exec_record'];h.w=w
n=0
def check(value):
 global n
 n+=1
 if not value:raise AssertionError('handoff vector '+str(n))
args=['e07aa706-1acd-4e65-b309-d7f330f79d54',19311,26219552,'36f1c62fe368414aea656a9173414708e3bb65f8dc1cd835c2f21de0523dfc12',['0']*4,set()]
check(h.owner_shape(*args))
for i in range(6):
 for value in [None,'foreign',1]:
  a=list(args);a[i]=value;check(not h.owner_shape(*a))
a=list(args);a[-1]={'19309'};check(not h.owner_shape(*a))
check(h.peer_shape([],[],False));check(h.peer_shape([],[],True))
batch={'pid':555,'usename':'schubert_batch','application_name':'PG496-fixed-recovery'}
snapshot={'pid':556,'usename':'schubert_migration','application_name':'PG496-fixed-snapshot'}
for peers in [[batch],[batch,snapshot]]:
 check(h.peer_shape(peers,[{'pid':555,'mode':'ExclusiveLock'}],False));check(not h.peer_shape(peers,[{'pid':555,'mode':'ExclusiveLock'}],True))
 for locks in [[],[{'pid':556,'mode':'ExclusiveLock'}],[{'pid':555,'mode':'ShareLock'}],[{'pid':555,'mode':'ExclusiveLock'}]*2]:check(not h.peer_shape(peers,locks,False))
check(h.peer_shape([snapshot],[],False));check(not h.peer_shape([snapshot],[],True))
for key in ['pid','usename','application_name']:
 for value in [None,'foreign']:
  bad=dict(batch);bad[key]=value;check(not h.peer_shape([bad],[{'pid':555,'mode':'ExclusiveLock'}],False))
for peers,locks in [(None,[]),([],None),([batch]*2,[{'pid':555,'mode':'ExclusiveLock'}]),([batch,snapshot,snapshot],[{'pid':555,'mode':'ExclusiveLock'}]),([],[{'pid':555,'mode':'ExclusiveLock'}])]:check(not h.peer_shape(peers,locks,False))
old={'Id':'caddy.service','LoadState':'loaded','InvocationID':'a'*32,'ExecMainStartTimestampMonotonic':'100','Type':'simple','Restart':'no','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no','MainPID':'42'}
current={**old,'MainPID':'0','ExecMainCode':'1','ExecMainStatus':'0'}
before={'ExecStart':'{ path=/bin/tool ; argv[]=/bin/tool literal ; ignore_errors=no ; start_time=[START] ; stop_time=[n/a] ; pid=42 ; code=(null) ; status=0/0 }','User':'fixed'}
after={'ExecStart':'{ path=/bin/tool ; argv[]=/bin/tool literal ; ignore_errors=no ; start_time=[START] ; stop_time=[END] ; pid=42 ; code=exited ; status=0 }','User':'fixed'}
check(h.same_configuration(before,after,old,current,'END'))
for original,replacement in [('path=/bin/tool','path=/bin/foreign'),('literal','foreign'),('ignore_errors=no','ignore_errors=yes'),('[START]','[CHANGED]'),('[END]','[OTHER]'),('pid=42','pid=43'),('code=exited','code=killed'),('status=0','status=143')]:
 v=dict(after);v['ExecStart']=v['ExecStart'].replace(original,replacement);check(not h.same_configuration(before,v,old,current,'END'))
for v in [None,{},dict(after,User='foreign'),dict(after,Unknown='x'),dict(after,ExecStart=None)]:check(not h.same_configuration(before,v,old,current,'END'))
for key in ['Id','LoadState','InvocationID','ExecMainStartTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL','ExecMainCode','ExecMainStatus']:
 v=dict(current);v[key]='foreign';check(not h.same_configuration(before,after,old,v,'END'))
print('PG497_HANDOFF_ORACLE assertions='+str(n)+' independent=true vmMutation0=true productionPT0=true')
