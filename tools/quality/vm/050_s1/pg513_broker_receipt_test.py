"""Independent full vendor/PID1 terminal receipt mutations. Synthetic, no VM."""
import ast,copy,json,pathlib,sys,types
from unittest.mock import patch
sys.modules.setdefault('dbus',types.SimpleNamespace())
import pg513_single_api_refs as h
from pg466_term_witness import FIELDS,unique
h.FIELDS=FIELDS;h.unique=unique
parsed=ast.parse(pathlib.Path(__file__).with_name('pg481_native_owned_stop.py').read_text())
defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in {'terminal','same_generation','broker_witness'}]
exec(compile(ast.Module(body=defs,type_ignores=[]),'<existing strict vendor witness>','exec'),h.__dict__)
before={'Id':'artemis.service','LoadState':'loaded','ActiveState':'active','SubState':'running','Job':'','MainPID':'38602','ControlPID':'0','InvocationID':'0608718743a74668a5e5bd87cf30f6b5','Type':'simple','Restart':'on-failure','RemainAfterExit':'no','Result':'success','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'3965781145','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0','ExecMainCode':'1','ExecMainStatus':'143','ExecMainExitTimestampMonotonic':'6000000000'}
row={'__CURSOR':'public-a','__MONOTONIC_TIMESTAMP':'5999999999','__REALTIME_TIMESTAMP':'1791391000000000','_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_SYSTEMD_UNIT':'artemis.service','_SYSTEMD_INVOCATION_ID':'0608718743a74668a5e5bd87cf30f6b5','PRIORITY':'6','_PID':'38602','_UID':'0','MESSAGE':'AMQ221002: Apache Artemis Message Broker version 2.56.0 [schubert-nk-broker] stopped, uptime 1 hour'}
manager={'__CURSOR':'public-b','__MONOTONIC_TIMESTAMP':'6000000001','__REALTIME_TIMESTAMP':'1791391000000001','_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'artemis.service','INVOCATION_ID':'0608718743a74668a5e5bd87cf30f6b5','MESSAGE_ID':'9d1aaa27d60140bd96365438aad20286','JOB_TYPE':'stop','JOB_RESULT':'done','MESSAGE':'public stopped fixture'}
checks=0
def check(v):
 global checks
 checks+=1
 if not v:raise AssertionError('independent shutdown receipt')
def execute(vendors,managers,ended=after):
 captures=[]
 def command(args):
  rows=vendors if any(x.startswith('_SYSTEMD_INVOCATION_ID=') for x in args) else managers
  return b''.join(json.dumps(v).encode()+b'\n' for v in rows)
 with patch.object(h,'command',command,create=True),patch.object(h,'save',lambda n,d:captures.append(n)),patch.object(h,'baseline',{'actors':{'artemis.service':{'authority':{'Uid':'0 0 0 0'}}}},create=True):
  try:h.broker_stop(before,ended);return captures,None
  except (ValueError,TypeError,KeyError) as error:return captures,error
saved,error=execute([row],[manager]);check(error is None and saved==['broker-vendor.private.jsonl','broker-manager.private.jsonl','broker-witness.private.json'])
for key in row:
 bad=dict(row);del bad[key];saved,error=execute([bad],[manager]);check(error is not None)
 bad=dict(row);bad[key]='' if key=='__CURSOR' else 'foreign';saved,error=execute([bad],[manager]);check(error is not None)
for key in ['_BOOT_ID','_UID','_COMM','INVOCATION_ID','MESSAGE_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP']:
 bad=dict(manager);del bad[key];saved,error=execute([row],[bad]);check(error is not None)
 bad=dict(manager);bad[key]='foreign';saved,error=execute([row],[bad]);check(error is not None)
for v,m in [([], [manager]),([row],[]),([row,row],[manager]),([row],[manager,manager])]:
 saved,error=execute(v,m);check(error is not None)
for key,value in [('InvocationID','f'*32),('MainPID','999'),('ExecMainCode','0'),('ExecMainStatus','0'),('Result','timeout'),('ExecMainExitTimestampMonotonic','0')]:
 bad=dict(after);bad[key]=value;saved,error=execute([row],[manager],bad);check(error is not None)
check(execute([row],[dict(manager,__MONOTONIC_TIMESTAMP='5999999999')])[1] is not None)
print('PG513_BROKER_RECEIPT_ORACLE independentAssertions='+str(checks)+' vendorPidUidAndWholeJournal=true pid1StopDone=true vmActions0=true productionPT0=true')
