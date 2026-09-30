"""Actual known failure + restored positive; strict non-secret capture, no S1 acceptance."""
import pathlib, subprocess, json, hashlib, shutil, datetime
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
source='d49a3a9fb0876ccf07e3e968df9e961bce215397'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==source
subprocess.run(['git','diff','--exit-code',source,'--','src','tools','pom.xml'],cwd=repo,check=True)
base=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG386-native-backup-failure'
assert not out.exists()
ssh=['ssh','-i','/home/mini/codex/project1/work/pgpt-vm/private/vm-access','-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/mini/codex/project1/work/pgpt-vm/private/known_hosts','ubuntu@127.0.0.1']
commands={
 'current-unit-state.txt':'sudo -n systemctl show schubert-nk-morning-controller.service schubert-nk-backup.service --property=Id,LoadState,ActiveState,SubState,Result,MainPID,ControlPID,InvocationID,ExecMainCode,ExecMainStatus,Job',
 'deployment-state.txt':'sudo -n readlink /opt/schubert-nk/current; sudo -n stat -c "%n %u:%g %a %h %s" /etc/schubert-nk/release-approval/current; sudo -n findmnt --target /opt/schubert-nk/releases/0.1.0-PG386 --output TARGET,FSTYPE,OPTIONS --noheadings; sudo -n find /run/schubert-nk/startup /run/schubert-nk/backup-request -maxdepth 1 -type f -printf "%f %s\\n"',
 'database.txt':'''sudo -n -u postgres psql -X -A -t -d schubert_nk -c "SELECT count(*),count(*) FILTER (WHERE NOT success),max(installed_rank) FROM schubert_meta.flyway_schema_history; SELECT id,step,attempt,to_char(started_at AT TIME ZONE 'UTC','YYYY-MM-DD\\\"T\\\"HH24:MI:SS.US\\\"Z\\\"'),to_char(ended_at AT TIME ZONE 'UTC','YYYY-MM-DD\\\"T\\\"HH24:MI:SS.US\\\"Z\\\"'),status,target_count,success_count,failure_count,byte_count,error_code FROM schubert.batch_runs ORDER BY id"''',
 'failed-part.txt':'sudo -n find /srv/schubert-nk/backup/20260930-125310-31100027-2222-4333-8444-555555555555.part -maxdepth 1 -printf "%f %y %s\\n"',
 'positive-MANIFEST.json':'sudo -n cat /srv/schubert-nk/backup/20260930-130116-31100027-2222-4333-8444-555555555555/MANIFEST.json',
 'restoration.txt':'sudo -n cmp -s /etc/schubert-nk/credentials/backup-pgpass /var/lib/pgpt-s1-preservation/pg386-original-backup-pgpass && echo EXACT_BYTES_RESTORED; sudo -n stat -c "%n %u:%g %a %h %s" /etc/schubert-nk/credentials/backup-pgpass /var/lib/pgpt-s1-preservation/pg386-original-backup-pgpass /var/lib/pgpt-s1-preservation/pg386-failed-backup-pgpass',
 'preservation-hashes.txt':'sudo -n sha256sum /var/lib/pgpt-s1-preservation/unit-originals-complete.tar /var/lib/pgpt-s1-preservation/db-pg381/schubert_nk-before-v023.dump /var/lib/schubert-nk/maintenance/runs/31100027-2222-4333-8444-555555555555.run',
 'environment.txt':'uname -sr; /usr/bin/java -version 2>&1; /usr/bin/pg_dump --version; /usr/bin/age --version',
 'worker-pid1-receipts.jsonl':'''sudo -n journalctl --since "2026-09-30 03:53:00 UTC" -o json --no-pager | python3 -c 'import sys,json
for line in sys.stdin:
 x=json.loads(line)
 if x.get("UNIT")=="schubert-nk-backup.service" and x.get("INVOCATION_ID"):
  print(json.dumps({k:x[k] for k in ["__REALTIME_TIMESTAMP","UNIT","INVOCATION_ID","JOB_TYPE","JOB_RESULT","_PID","_EXE"] if k in x}))' '''
}
out.mkdir(parents=True)
actual={}
for name,command in commands.items():
 p=subprocess.run(ssh+[command],text=True,capture_output=True,check=True)
 assert not p.stderr.strip(),name
 (out/name).write_text(p.stdout)
 actual[name]={'command':command,'exitCode':0}
for name in ['pg386-failed-unit-state.log','pg386-failed-parent.exec','pg386-failed-backup.exec','pg386-positive-parent.exec','pg386-positive-backup.exec']:
 shutil.copyfile(base/name,out/name)
rows=[json.loads(s) for s in (out/'worker-pid1-receipts.jsonl').read_text().splitlines()]
assert all(x['_PID']=='1' and x['_EXE']=='/usr/lib/systemd/systemd' for x in rows)
positive={x['INVOCATION_ID'] for x in rows if x.get('JOB_TYPE')=='start' and x.get('JOB_RESULT')=='done' and x['INVOCATION_ID']!='98336502bb5f4764b378eccea15979f3'}
assert len(positive)==1
positive=positive.pop()
assert any(x['INVOCATION_ID']==positive and x.get('JOB_TYPE')=='stop' and x.get('JOB_RESULT')=='done' for x in rows)
db=(out/'database.txt').read_text()
assert '7|BACKUP_DB|4|2026-09-30T03:53:10.245655Z|2026-09-30T03:53:12.364635Z|FAILED|1|0|1|0|COMMAND_FAILURE' in db
assert '8|BACKUP_CONFIG|4|2026-09-30T03:53:10.245655Z|2026-09-30T03:53:12.364635Z|FAILED|1|0|1|0|COMMAND_FAILURE' in db
assert '9|BACKUP_DB|5|2026-09-30T04:01:16.189175Z|2026-09-30T04:01:22.481527Z|SUCCESS|1|1|0|170930|' in db
assert '10|BACKUP_CONFIG|5|2026-09-30T04:01:16.189175Z|2026-09-30T04:01:22.481527Z|SUCCESS|2|2|0|61640|' in db
assert 'EXACT_BYTES_RESTORED' in (out/'restoration.txt').read_text()
assert 'MANIFEST.json' not in (out/'failed-part.txt').read_text()
manifest={'id':'PG386-native-backup-failure','formal':False,'sourceCommit':source,'branch':'dev-foundation','executionTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'testIds':['PT-OPS-BFAILED-VM001','PT-OPS-BFAILED-VM002','PT-OPS-MMAIN009','PT-OPS-MMAIN010'],
 'input':'genuine source external Morning --resume, preserved original and old rows; isolated incorrect private Backup pgpass then exact restoration; no clock/schema/result fabrication',
 'expected':'fresh normal nonzero Backup exit -> both exact FAILED/COMMAND_FAILURE -> independent readback -> original/request/intent retirement; no false archive; restored positive new fresh worker',
 'actual':{'failedParentInvocation':'58161ad0006a4fb6909d4a74d6cd0b62','failedWorkerInvocation':'98336502bb5f4764b378eccea15979f3','workerExecMainCode':1,'workerExecMainStatus':1,'failedRows':[7,8],'failedAttempt':4,'positiveParentInvocation':'90999e2a66954050b835d49a89475c89','positiveWorkerInvocation':positive,'positiveRows':[9,10],'positiveAttempt':5,'credentialRestoredExact':True,'permitsIssued':0,'externalMorningExit':30,'S1Accepted':False},
 'commands':actual,'bugs':['BUG-325','BUG-349'],'ssc':['SSC-115'],'coverage':{'allFour100Percent':False,'sameByteUnion':'captured separately; no historical exec merge'},
 'limitations':['whole S1 and formal53scope not accepted','normal successful resume SKIP and failure subsequent Cleanup/Transfer/Expiry/issuer pending','real30min timeout/recovery not executed','private credential originals/archive/dump/signing and decryption keys stay outside Git'],
 'redaction':'only fixed metadata/counters/coverage/manifest; no credential hash/value, raw journal message, token/session/password/private key or dump'}
manifest['files']=[{'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file()]
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'positiveWorkerInvocation':positive,'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formal':False}))
