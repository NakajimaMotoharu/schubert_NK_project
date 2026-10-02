"""Non-secret initial deployment and positive actual Backup roundtrip capture; never S1 acceptance."""
import pathlib, subprocess, json, hashlib, shutil, datetime
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG385-native-deployment'
assert not out.exists()
ssh=['ssh','-i','/home/mini/codex/project1/work/pgpt-vm/private/vm-access','-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/mini/codex/project1/work/pgpt-vm/private/known_hosts','ubuntu@127.0.0.1']
commands={
 'unit-state.txt':'sudo -n systemctl show schubert-nk-morning-controller.service schubert-nk-backup.service --property=Id,LoadState,ActiveState,SubState,Result,MainPID,ControlPID,InvocationID,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,Job',
 'deployment-state.txt':'sudo -n readlink /opt/schubert-nk/current; sudo -n stat -c "%n %u:%g %a %h %s" /etc/schubert-nk/release-approval/current; sudo -n findmnt --target /opt/schubert-nk/releases/0.1.0-PG385 --output TARGET,FSTYPE,OPTIONS --noheadings; sudo -n find /run/schubert-nk/startup /run/schubert-nk/backup-request -maxdepth 1 -type f -printf "%f %s\\n"',
 'schema-and-backup.txt':'''sudo -n -u postgres psql -X -A -t -d schubert_nk -c "SELECT count(*),count(*) FILTER (WHERE NOT success),max(installed_rank) FROM schubert_meta.flyway_schema_history; SELECT step,attempt,status,error_code,ended_at IS NULL FROM schubert.batch_runs ORDER BY step,attempt"''',
 'preservation-hashes.txt':'sudo -n sha256sum /var/lib/pgpt-s1-preservation/unit-originals-complete.tar /var/lib/pgpt-s1-preservation/db-pg381/schubert_nk-before-v023.dump /var/lib/schubert-nk/maintenance/runs/31100027-2222-4333-8444-555555555555.run',
 'environment.txt':'uname -sr; /usr/bin/java -version 2>&1; /usr/bin/pg_dump --version; /usr/bin/age --version',
}
out.mkdir(parents=True)
actual={}
for name,command in commands.items():
 p=subprocess.run(ssh+[command],text=True,capture_output=True,check=True)
 assert not p.stderr.strip(), name
 (out/name).write_text(p.stdout)
 actual[name]={'command':command,'exitCode':p.returncode}
shutil.copyfile('/home/mini/codex/project1/work/pgpt-runs/PG379/pg385-morning-first.exec',out/'morning-first.exec')
shutil.copyfile('/home/mini/codex/project1/work/pgpt-runs/PG379/pg385-backup-first.exec',out/'backup-first.exec')
shutil.copyfile('/home/mini/codex/project1/work/pgpt-runs/PG379/pg385-artifact-oracle.json.log',out/'artifact-oracle.txt')
hashes=[{'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file()]
manifest={
 'id':'PG385-native-deployment','formal':False,'executionTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'sourceCommit':'a6b5c7c8b021c4b391b3af90572eab5d0eac8ab1','branch':'dev-foundation',
 'input':'fixed separately pinned Ed25519 signature; actual 177 artifact/61 dependencies/23 SQL release; pre-V023 private restore point; preserved original same run',
 'expected':'signature+full RO BOM verified before approval; dedicated V023 migrate exactly1/post validate; atomic absolute current selector+root400 approval and Production full BOM readback; external Morning actual backup roundtrip',
 'actual':{'pinnedSignature':'PASS','hostReadOnlyFullBom':'PASS after BUG342','dedicatedV023Migration':'PASS after BUG343','currentAndRootApprovalReadback':'PASS after BUG341','externalMorning':'Backup SUCCESS roundtrip; final exit30 because S2/S3 are not assembled','externalInvocation':'68b5e9d1bda54e21b808a7325838a22a','workerInvocation':'a7d870091a45446fa19aa1506b01783f','workerInvocations':1,'databaseBackupBegins':6,'requestBytes':0,'parentCoverageBytes':'actual file hash/size below','permitsIssued':0,'S1Accepted':False},
 'commands':actual,'bugs':['BUG-340','BUG-341','BUG-342','BUG-343','BUG-344','BUG-345','BUG-347'],'ssc':['SSC-110','SSC-112','SSC-113'],
 'coverage':{'instrumentation':'JaCoCo0.8.15 genuine Morning classpath/source byte; cold capture reachability only','allFour100Percent':False},
 'files':hashes,'limitations':['support checks only, no formal PT/IT/ST/whole S1 claim','worker/dump/archives/MANIFEST/DB bothSUCCESS/request and intent retirement positive; native timeout/failure not accepted','final Morning exit30 is partial-only, never startup PASS; prior failed attempts retained','restore dump/signing key/age private key/credential originals remain Git-external private'],
 'redaction':'metadata/hash/state only; no journal messages/DB payload/credential/session/token/password/private key/dump; exec contains only coverage probe bitmaps'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':manifest['id'],'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'S1Accepted':False}))
