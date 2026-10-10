"""Fresh read-only exact full source/post trigger for finite runtime retirement."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1220_current_full32_terminal_post import payload as previous
from pg1223_completed_runtime_contract import TARGET,SHA

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

def payload():
    s=previous();s=s[:s.index("save=base/'pg1220-terminal-final-v1'")]
    s=s.replace("'run':'PG1220-terminal-final-v1'","'run':'PG1222-completed-retirement-preflight-v1'")
    s+='\n'+EXTRA
    compile(s,'<full current retirement readonly preflight>','exec');return s

EXTRA=r'''
target=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf')
require(hashlib.sha256(target.read_bytes()).hexdigest()=='d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0')
require(target.stat().st_size==647)
u='schubert-nk-inbox-inspector.service'
j=command(['journalctl','--boot=cbca87383b244090b77cbf029677cdd6','_PID=1','UNIT='+u,'-o','json','--no-pager'])
require(j==b'' and not list(pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-inspector196').glob('*.exec')))
business_date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()
require(str(business_date)>'2026-10-10')
result.update(currentInspectorPid1Records=0,currentInspectorNativeFiles=0,journalSha256=hashlib.sha256(j).hexdigest(),newJstDate=str(business_date),currentResumeRuntimeSha256=hashlib.sha256(target.read_bytes()).hexdigest(),normalCurrentNewScopesSealed=True,allFull32=True,mutationAuthority=False)
result.pop('proofHashes',None);result.pop('toolHashes',None)
print(json.dumps(result))
'''

def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current source required')
    os.umask(0o077);base=W/'pg1222-completed-retirement-preflight-v1'
    if any(Path(str(base)+x).exists()for x in ['.safe.json','.private.log','.exit']):raise ValueError('new-only readonly slot required')
    build=json.loads((W/'pg1217-frozen-v1.safe.json').read_bytes())
    names=['Pg1216NativeStop.class','Pg1216NativeStop$References.class','pg1216_native_refs.py','pg1216_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1216_parent_receipt.py','pg1216_durable.py','pg1216_configuration.py','pg1216_configuration_capture.py','pg1216_row_bound.py','pg1216_stable_journal.py']
    hashes={n:build['fileHashes'][n]for n in names};receipt=(W/'pg1216-native-tools-v1/pg1216_parent_receipt.py').read_text()
    code='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    value={'actualExit':r.returncode,'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode

if __name__=='__main__':raise SystemExit(main())
