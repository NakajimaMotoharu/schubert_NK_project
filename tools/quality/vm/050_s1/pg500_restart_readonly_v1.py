"""PG500 / N11: management-only current-boot reauthentication, private values only."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

os.umask(0o077)
assert sys.argv[1:] in ([], ['--corrected-v2'])
private = Path('/home/mini/codex/project1/work/pgpt-vm/private')
options = ['-i', str(private / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(private / 'known_hosts'),
           '-oConnectTimeout=5', '-p', '22222', 'ubuntu@127.0.0.1']
payload = r'''
import datetime,hashlib,json,os,pathlib,stat,subprocess,re
os.umask(0o077)
assert os.geteuid()==0
def command(args,limit=8*1024*1024):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 assert p.returncode==0 and len(p.stdout)<=limit
 return p.stdout
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly/refs-after.private.json')
raw=base.read_bytes();assert hashlib.sha256(raw).hexdigest()=='1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3'
baseline=json.loads(raw)
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert boot!='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
fields='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
units={}
for name in baseline['units']:
 assert re.fullmatch(r'(?:schubert-nk-[a-z-]+|caddy|artemis)\.service',name)
 def read():
  value={}
  for line in command(['/usr/bin/systemctl','show',name,'--property='+fields]).decode('ascii').splitlines():
   key,text=line.split('=',1);assert key not in value;value[key]=text
  assert set(value)==set(fields.split(',')) and value['Id']==name and value['LoadState']=='loaded'
  assert value['MainPID']==value['ControlPID']=='0' and value['Job']==value['InvocationID']==''
  assert value['ActiveState']=='inactive' and value['SubState']=='dead' and value['Result']=='success'
  assert all(value[k]=='0' for k in ['ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic'])
  assert value['KillMode']=='control-group' and value['SendSIGKILL']=='no'
  return value
 first=read();cgroup=pathlib.Path('/sys/fs/cgroup/system.slice')/name
 if cgroup.exists():
  for p in [cgroup,*[d for d in cgroup.rglob('*') if d.is_dir()]]:
   assert not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text()
 assert first==read();units[name]=first
tables=baseline['rows'];assert len(tables)==24 and len(tables['schubert.batch_runs'])==442
sql="begin isolation level repeatable read read only;set local timezone='UTC';"
for t in tables:
 assert re.fullmatch(r'[a-z_]+\.[a-z_]+',t)
 sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
sql+='commit;'
def database():
 result={}
 # BUG809/YKT578: full-DB readback is the prior fixed 32MiB contract, not small metadata.
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],32*1024*1024).splitlines():
  v=json.loads(line);assert v['table'] not in result;result[v['table']]=v['rows']
 assert result==tables
 return result
rows=database();assert rows==database()
runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
current=pathlib.Path('/opt/schubert-nk/current').readlink()
assert str(current)=='/opt/schubert-nk/releases/0.1.0-PG495' and str(current)==baseline['current']
record={'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'boot':boot,'units':units,'rows':rows,
 'runtimePresent':runtime.exists(),'startupPresent':pathlib.Path('/run/schubert-nk/startup').exists(),
 'baselineTrees':baseline['trees'],'current':str(current),'source':'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c'}
target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg500-cold-readonly')
assert not target.exists();target.mkdir(mode=0o700)
with (target/'current.private.json').open('x') as f:
 os.fchmod(f.fileno(),0o600);json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'currentBoot':boot,'unitCount':len(units),'coldFull18TwoRead':True,'databaseTables':len(rows),
 'batchRows':len(rows['schubert.batch_runs']),'fullRowsEqual':True,'runtimePresent':runtime.exists(),
 'startupPresent':record['startupPresent'],'oldRuntimeRetirementProven':False,
 'baselineKeys':list(baseline),'treeRoots':list(baseline['trees']),
 'treeShapes':{k:type(v).__name__ for k,v in baseline['trees'].items()},'current':'PG495','mutations':0}))
'''
version = 'v2' if sys.argv[1:] else 'v1'
log = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg500-restart-readonly-' + version + '.private.log')
assert not log.exists()
with log.open('xb') as handle:
    result = subprocess.run(['ssh', *options, 'sudo -n python3 -B -'],
                            input=payload.encode(), stdout=handle, stderr=handle, timeout=120)
if result.returncode == 0:
    summary = json.loads(log.read_text())
    print(json.dumps(summary))
else:
    print(json.dumps({'result': 'NOT_ACCEPTED', 'exitCode': result.returncode,
                      'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest()}))
raise SystemExit(result.returncode)
