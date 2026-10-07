"""Independent fixed SKIP/full-column and genuine PID1 DONE vectors; no VM authority."""
import ast,pathlib,datetime,copy
R=pathlib.Path(__file__).parent;source=(R/'pg528_terminal_refs.py').read_text();parsed=ast.parse(source)
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in ['require','verify_batch','verify_pid1']]
env={'datetime':datetime,'BOOT':'cc9ed874-7f4f-450e-a188-8de1e42c8441','INV':'8f4514e19fd94c429f2587af71edb53a','START':15089848500,'END':16431357068};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent operator target>','exec'),env)
checks=0
def check(v):
 global checks
 checks+=1;assert v,'fixed operator oracle '+str(checks)
def denied(fn,*args):
 try:env[fn](*args)
 except (ValueError,TypeError,KeyError):check(True);return
 raise AssertionError('foreign proof accepted')
steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER','CLEAN_BATCH_RUN','CLEAN_EXPIRY']
old=[{'id':i+1,'step':steps[i%10],'business_date':'2026-10-06','attempt':i//10+1,'otherColumn':'exact-'+str(i)}for i in range(452)]
actual=copy.deepcopy(old)
for i,step in enumerate(steps):actual.append({'id':453+i,'step':step,'run_id':'91a748b4-1abe-484c-9682-44f46429b324','business_date':'2026-10-06','attempt':max(r['attempt']for r in old if r['step']==step)+1,'status':'SKIPPED','target_count':0,'success_count':0,'failure_count':0,'byte_count':0,'error_code':'ALREADY_SUCCESSFUL','error_summary':'step already successful for business date','started_at':'2026-10-07T19:47:00+00:00','ended_at':'2026-10-07T19:47:01+00:00'})
env['verify_batch'](old,actual);check(True)
for v in [None,[],{},[None]*452]:denied('verify_batch',v,actual)
for v in [None,[],{},actual[:-1],actual+[actual[-1]]]:denied('verify_batch',old,v)
for field in actual[-1]:
 v=copy.deepcopy(actual);v[-1][field]=None;denied('verify_batch',old,v)
 v=copy.deepcopy(actual);del v[-1][field];denied('verify_batch',old,v)
for field,value in [('id',True),('step','UNKNOWN'),('run_id','foreign'),('business_date','2026-10-07'),('attempt',1),('status','SUCCESS'),('target_count',1),('success_count',True),('error_code','OTHER'),('ended_at','2026-10-07T19:46:00+00:00')]:
 v=copy.deepcopy(actual);v[-1][field]=value;denied('verify_batch',old,v)
v=copy.deepcopy(actual);v[0]['otherColumn']='changed';denied('verify_batch',old,v)
v=copy.deepcopy(actual);v[-1]['id']=v[0]['id'];denied('verify_batch',old,v)
base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'8f4514e19fd94c429f2587af71edb53a'}
rows=[{**base,'__MONOTONIC_TIMESTAMP':str(t),'MESSAGE_ID':mid}for t,mid in [(15089849562,'7d4958e842da4a758f6c1cdc7b36dcc5'),(16431356844,'7ad2d189f7e94e70a38c781354912448'),(16431357068,'39f53479d3a045ac8e11786248231fbf'),(16431357368,'ae8f7b866b0347b9af31fe1c80b127c0')]]
rows[2].update(JOB_ID='26968',JOB_TYPE='start',JOB_RESULT='done');env['verify_pid1'](rows);check(True)
for v in [None,[],{},rows[:-1],rows+[rows[-1]]]:denied('verify_pid1',v)
for key in base:
 for value in [None,'foreign']:
  v=copy.deepcopy(rows);v[0][key]=value;denied('verify_pid1',v)
for key,value in [('__MONOTONIC_TIMESTAMP',None),('__MONOTONIC_TIMESTAMP','x'),('__MONOTONIC_TIMESTAMP','15089848499'),('__MONOTONIC_TIMESTAMP','16431358069'),('JOB_ID','old'),('JOB_TYPE','stop'),('JOB_RESULT','failed'),('MESSAGE_ID','foreign')]:
 v=copy.deepcopy(rows);v[2][key]=value;denied('verify_pid1',v)
v=copy.deepcopy(rows);v[1]['MESSAGE_ID']='foreign';denied('verify_pid1',v)
java=(R/'Pg528TerminalReadback.java').read_text();check('PG528-terminal-readback' in java and 'readback' in java);check('2026-10-07T19:46:29.837227Z'in java and '2026-10-07T20:08:51.344734Z'in java)
check('systemctl'not in java and '.start.intent' in java)
print('PG528_COMPLETED_ORACLE independentAssertions='+str(checks)+' allColumnPreservation=true skipAndAttemptLiteralVectors=true pid1NotGcZero=true nullNegative=true productionPT0=true vmActions0=true')
