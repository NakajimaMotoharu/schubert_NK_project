"""Readonly full current partial-failed Root capture, no authority/stop/repair."""
import ast
import hashlib
import json
import os
import subprocess
from pg1441_current_cold_refs import source
from pg1450_current_cold_retry import W
from pg1446_current_cold_stage import SSH


def payload():
    raw=source().split('import dbus,time,sys,types\n',1)[0]
    tree=ast.parse(raw)
    tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef)or n.name!='snapshot']
    raw=ast.unparse(tree)+'\n'+BODY
    ast.parse(raw);return raw


BODY=r'''
import dbus
os.umask(0o077)
SAVE=BASE/'pg1464-failed-current-capture-v1';SAVE.mkdir(mode=0o700)
def snapshot():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and not pathlib.Path('/proc/6873').exists())
 units={n:show(n)for n in UNITS};m=units['schubert-nk-morning-controller.service']
 require(m['ActiveState']==m['SubState']=='failed' and m['Result']=='timeout' and m['ExecMainCode']=='1'and m['ExecMainStatus']=='143'and m['MainPID']==m['ControlPID']=='0'and m['Job']=='' and m['InvocationID']=='1ee3b3e121c74e63ae28fe4d912e9ede' and m['ExecMainStartTimestampMonotonic']=='5711141318')
 configuration={}
 for n in UNITS:
  value=complete_configuration(command(['systemctl','show',n,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),n)
  require(CONFIG_CONTRACT['same'](old['configuration'][n],value,exec_record));configuration[n]=value
 broker=units['artemis.service'];require(broker['MainPID']=='41805'and broker['InvocationID']=='47be234990bd4aec838648a8f365536f'and broker['ExecMainStartTimestampMonotonic']=='6366634712'and broker['ActiveState']=='active'and broker['SubState']=='running')
 p=pathlib.Path('/proc/41805');require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==636663 and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='2a7089f6e2bbbbe31a74253fab119bd63b0055019e386c3a6f372a19d6e004b6')
 actor={'pid':41805,'ticks':636663,'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'exe':str((p/'exe').readlink()),'status':(p/'status').read_text(),'cgroup':(p/'cgroup').read_text(),'fds':{f.name:str(f.readlink())for f in(p/'fd').iterdir()}}
 # Actor status runtime counters vary, capture privately but don't use these
 # counters as stable authority. Fixed manager/kernel identity is checked twice.
 actor['statusSha256']=hashlib.sha256(actor.pop('status').encode()).hexdigest()
 durable={k:tree(pathlib.Path(os.path.commonpath(list(old[k]))))for k in['backup','credentials','originals','oldProofs']}
 require(durable['credentials']==old['credentials']and durable['oldProofs']==old['oldProofs'])
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in old['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table) is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 sql+='commit;';rows={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],67108864).splitlines():
  value=json.loads(line);require(value['table']not in rows);rows[value['table']]=value['rows']
 require(len(rows)==24)
 peers=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"],4096)
 require(peers.splitlines()==[b'0',b'0'])
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292');require(pathlib.Path('/opt/schubert-nk/current').readlink()==release)
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM);data=json.loads(manifest);require(data['source']['commit']==SOURCE and len(data['artifacts'])==187)
 command(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-rawin','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(BASE/'pg1292-manifest.sig')],4096)
 artifacts={}
 for record in data['artifacts']:
  file=release/record['path'];m=metadata(file);require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1 and m[6]==record['size'] and hashlib.sha256(file.read_bytes()).hexdigest()==record['sha256'] and metadata(file)==m);artifacts[record['path']]=record['sha256']
 for file,expected in old['unitFilesActual'].items():
  p=pathlib.Path(file);m=metadata(p);require(UNIT_VECTOR['matches'](expected,m,hashlib.sha256(p.read_bytes()).hexdigest())and metadata(p)==m)
 runtime={n:tree(pathlib.Path('/run/schubert-nk')/n)for n in['startup','backup-request','cleanup-request','expiry-request','maintenance','pt-coverage']}
 active=pathlib.Path('/var/lib/schubert-nk/maintenance/active');expected=b'NKACT1\n15700a87-9117-4f63-a0ff-768dd604d0f1\n2026-10-11T21:18:59.040097Z\n9e706936-a3c9-4a09-bb66-e2b1e8bbef66\n'
 require(active.read_bytes()==expected and not(pathlib.Path('/var/lib/schubert-nk/maintenance/attempts')/'9e706936-a3c9-4a09-bb66-e2b1e8bbef66.done').exists())
 return {'source':SOURCE,'boot':BOOT,'manifestSha256':BOM,'units':units,'configuration':configuration,'durable':durable,'rows':rows,'runtime':runtime,'artifacts':artifacts,'brokerActor':actor}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for n in UNITS:manager.LoadUnit(n);manager.RefUnit(n);refs.append(n)
 first=snapshot();second=snapshot()
 # Volatile /proc status digest is diagnostic, not generation/ownership oracle.
 first['brokerActor'].pop('statusSha256');second['brokerActor'].pop('statusSha256');require(first==second)
finally:
 failures=[]
 for n in reversed(refs):
  try:manager.UnrefUnit(n)
  except Exception as e:failures.append(type(e).__name__)
 try:bus.close()
 except Exception as e:failures.append(type(e).__name__)
 require(not failures)
encoded=json.dumps(first,sort_keys=True).encode()
with(SAVE/'observed.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
print(json.dumps({'run':'PG1464-failed-current-capture-v1','actualExit':0,'source':SOURCE,'boot':BOOT,'parentFailed143':True,'activeOriginalRetained':True,'newDoneAbsent':True,'full24DbCaptured':True,'tenFull18Full32Twice':True,'signature187Verified':True,'brokerStillOwnedProofPending':True,'allMetadataRefsClosed':True,'permissionIssued':False,'stopRevokeRetirementIssued':False,'formalAccepted':False,'privateSha256':hashlib.sha256(encoded).hexdigest(),'durableCounts':{k:len(v)for k,v in first['durable'].items()}},sort_keys=True))
'''


def main():
    os.umask(0o077);out=W/'pg1464-failed-current-capture-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
