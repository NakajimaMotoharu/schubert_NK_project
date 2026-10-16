"""Fresh failed state plus immutable original PID1 journal/done; data only, no stop permission."""
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg4070_failed_root_resource_read import payload as accounting
import pg4074_failed_done_parent_contract as contract


def payload():
    raw = accounting(); raw = raw[:raw.index("value={'actualExit':0")]
    return raw + '\nCONTRACT_SOURCE=' + repr(inspect.getsource(contract)) + '\n' + r'''
contract={};exec(CONTRACT_SOURCE,contract)
base=Path('/var/lib/pgpt-s1-preservation/pg4076-failed-done-parent-read-v1');assert not os.path.lexists(base);os.umask(0o077);base.mkdir(mode=0o700)
saved=Path('/var/lib/pgpt-s1-preservation/pg4072-failed-parent-pid1-read-v1/pid1.private.jsonl').read_bytes();assert hashlib.sha256(saved).hexdigest()=='4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38'
def unique(pairs):
 value={}
 for k,v in pairs:
  if k in value:raise ValueError('duplicate actual journal field')
  value[k]=v
 return value
records=[json.loads(line,object_pairs_hook=unique)for line in saved.splitlines()]
keys=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
records=[{k:v[k]for k in keys if k in v}for v in records if 128735401165<=int(v['__MONOTONIC_TIMESTAMP'])<=130545470134]
props='Id,LoadState,ActiveState,SubState,InvocationID,MainPID,ControlPID,Job,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic'
def state():
 r=subprocess.run(['systemctl','show','schubert-nk-morning-controller.service','--property='+props],capture_output=True,text=True,timeout=10);assert r.returncode==0
 return dict(line.split('=',1)for line in r.stdout.splitlines())
before=state();donepath=Path('/var/lib/schubert-nk/maintenance/attempts/d9d58371-bf80-49f6-bad9-3d1e0916fb04.done');done=donepath.read_bytes()
classification=contract['classify'](data['source']['commit'],sha,boot,before,records,done)
group=Path('/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service')
if group.exists():
 for p in [group,*[x for x in group.rglob('*')if x.is_dir()]]:
  assert not(p/'cgroup.procs').read_text().strip()and 'populated 0\n'in(p/'cgroup.events').read_text()
assert not Path('/proc/696557').exists()and before==state()and donepath.read_bytes()==done and first==read()and manifest.read_bytes()==raw
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':classification,'actualPid1Records':len(records),'historicalPid1JournalSha256':hashlib.sha256(saved).hexdigest(),'contractSha256':hashlib.sha256(CONTRACT_SOURCE.encode()).hexdigest(),'oldRootPidAndCgroupEmpty':True,'sameFailedStateAndOriginalTwice':True,'stateChangingActions':0,'authorityIssued':False,'formalAccepted':False}
(base/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077); out = W / 'pg4076-failed-done-parent-read-v1'; out.mkdir()
    raw = payload(); compile(raw, '<failed-DONE data only>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=60)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': contract.SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if not r.returncode: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
