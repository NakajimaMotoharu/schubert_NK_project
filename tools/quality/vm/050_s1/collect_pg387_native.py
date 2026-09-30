"""Real normal resume: fresh validation worker + immutable original + separate current SKIP."""
import pathlib,subprocess,json,hashlib,datetime,shutil
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
base=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG387-native-normal-resume'
assert not out.exists()
ssh=['ssh','-i','/home/mini/codex/project1/work/pgpt-vm/private/vm-access','-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/mini/codex/project1/work/pgpt-vm/private/known_hosts','ubuntu@127.0.0.1']
artifact='/srv/schubert-nk/backup/20260930-130116-31100027-2222-4333-8444-555555555555'
immutable='''sudo -n stat -c "%n %d %i %u:%g %a %h %s %y %z" ART/MANIFEST.json ART/schubert_nk.dump ART/config.tar ART/credentials.tar.age; sudo -n sha256sum ART/{MANIFEST.json,schubert_nk.dump,config.tar,credentials.tar.age}; sudo -n -u postgres psql -X -A -t -d schubert_nk -c "SELECT id,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary FROM schubert.batch_runs WHERE id IN (9,10) ORDER BY id"; sudo -n find /srv/schubert-nk/backup -maxdepth 1 -type d -printf "%f\\n" | sort'''.replace('ART',artifact)
commands={
 'after-original.txt':immutable,
 'current-skips.txt':'''sudo -n -u postgres psql -X -A -t -d schubert_nk -c "SELECT id,run_id,step,attempt,status,target_count,success_count,failure_count,byte_count,error_code,error_summary,ended_at=started_at FROM schubert.batch_runs WHERE attempt=6 ORDER BY id"''',
 'deployment-and-retirement.txt':'sudo -n readlink /opt/schubert-nk/current; sudo -n find /run/schubert-nk/backup-request /run/schubert-nk/startup -maxdepth 1 -type f -printf "%f %s\\n"; sudo -n systemctl show schubert-nk-morning-controller.service schubert-nk-backup.service --property=Id,MainPID,ControlPID,ActiveState,SubState,Job,Result,ExecMainCode,ExecMainStatus,InvocationID',
 'fresh-worker.jsonl':'''sudo -n journalctl --since "2026-09-30 05:15:00 UTC" -o json --no-pager | python3 -c 'import sys,json
for line in sys.stdin:
 x=json.loads(line)
 if x.get("UNIT")=="schubert-nk-backup.service" and x.get("INVOCATION_ID")=="01cd3703bf834fcfa27dbf1287e8f9ae":
  print(json.dumps({k:x[k] for k in ["__REALTIME_TIMESTAMP","UNIT","INVOCATION_ID","JOB_TYPE","JOB_RESULT","_PID","_EXE"] if k in x}))' '''
}
out.mkdir(parents=True)
for name,command in commands.items():
 p=subprocess.run(ssh+[command],text=True,capture_output=True,check=True)
 assert not p.stderr.strip(),name
 (out/name).write_text(p.stdout)
assert (out/'after-original.txt').read_bytes()==(base/'pg387-before-reuse-state.log').read_bytes()
skips=(out/'current-skips.txt').read_text()
assert skips.splitlines()==[
 '11|31100027-2222-4333-8444-555555555555|BACKUP_DB|6|SKIPPED|0|0|0|0|ALREADY_SUCCESSFUL|step already successful for business date|t',
 '12|31100027-2222-4333-8444-555555555555|BACKUP_CONFIG|6|SKIPPED|0|0|0|0|ALREADY_SUCCESSFUL|step already successful for business date|t']
receipts=[json.loads(s) for s in (out/'fresh-worker.jsonl').read_text().splitlines()]
assert all(x['_PID']=='1' and x['_EXE']=='/usr/lib/systemd/systemd' for x in receipts)
assert any(x.get('JOB_TYPE')=='start' and x.get('JOB_RESULT')=='done' for x in receipts)
assert any(x.get('JOB_TYPE')=='stop' and x.get('JOB_RESULT')=='done' for x in receipts)
retired=(out/'deployment-and-retirement.txt').read_text()
assert 'backup-request ' not in retired and 'backup-start.intent ' not in retired and 'permit' not in retired
for src,dst in [('pg387-before-reuse-state.log','before-original.txt'),('pg387-parent.exec','parent.exec'),('pg387-backup.exec','backup.exec'),('pg387-batch-union.json','batch-host-native-union.json'),('pg387-native-unit-state.log','native-unit-state.txt')]:
 shutil.copyfile(base/src,out/dst)
m={'id':'PG387-native-normal-resume','formal':False,'sourceCommit':'7ba352d6f0b7c08c371e838683fb6c2ba58725af','branch':'dev-foundation','executionTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'environment':'actual Ubuntu26.04/kernel7.0.0-34/JDK25.0.4/PostgreSQL18.6/JaCoCo0.8.15; fixed signed releasePG387/full hostRO BOM177/61/23',
 'testIds':['PT-OPS-BRESUME-VM001','PT-OPS-BVERIFY003'],
 'input':'same original run/cutoff, genuine external Morning --resume, prior SUCCESS bundle rows9+10/attempt5; existing coverage-only dropins, no fake worker/result/permit',
 'expected':'same original four file bytes/hash/inode/metadata and old DB full rows; same directory inventory; fresh actual validation-only worker; separate current rows11+12/attempt6 SKIPPED ALREADY_SUCCESSFUL all0; request/intent retired',
 'actual':{'originalByteMetadataAndDatabaseUnchanged':True,'directoryInventoryUnchanged':True,'currentRows':[11,12],'currentAttempt':6,'workerInvocation':'01cd3703bf834fcfa27dbf1287e8f9ae','parentInvocation':'2144cbd6195e47cd8d2833576e704372','requestAndIntentRetired':True,'permitsIssued':0,'externalMorningExit':30,'S1Accepted':False},
 'commands':{n:{'command':c,'exitCode':0} for n,c in commands.items()},'bugs':['BUG-350'],'ssc':['SSC-116'],'coverage':json.loads((out/'batch-host-native-union.json').read_text()),
 'limitations':['whole S1/real30min timeout and S2/S3 still incomplete','allfour coverage100%/formal53scope not accepted','systemd fixed LoadCredential copy remains; application pgpass read/copy and archive/dump generation are not invoked','no prior-source exec union'],
 'redaction':'fixed unit/PID1 fields, counters, hashes and probe bitmaps only; no private key/password/session/token/dump/plain credential archive/raw journal message'}
m['files']=[{'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file()]
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('PG387 native manifestSha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
