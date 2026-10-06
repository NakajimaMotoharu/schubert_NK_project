"""One owned PG495 pending code-only publication. No start, epoch, DDL or DB write."""
import datetime,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c';DIGEST='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
assert (W/'pg495-six-full-v1.source').read_text().strip()==SOURCE and (W/'pg495-six-full-v1.exit').read_text().strip()=='0'
base=W/'pg498-pending-native-v1';assert not pathlib.Path(str(base)+'.started').exists()
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
prefixes=['pg498-pending-tools-v1','pg490-migration-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG489/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG489/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG489/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG489/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
with pathlib.Path(str(base)+'.started').open('x') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');f.flush();os.fsync(f.fileno())
with pathlib.Path(str(base)+'.private.log').open('xb') as f:
 test=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg498PendingDeploymentTest'],stdout=f,stderr=f);assert test.returncode==0
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg498PendingDeployment '+SOURCE+' '+DIGEST],stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
for suffix,value in [('.exit',str(result.returncode)),('.completed',datetime.datetime.now(datetime.timezone.utc).isoformat())]:
 with pathlib.Path(str(base)+suffix).open('x') as f:f.write(value+'\n');f.flush();os.fsync(f.fileno())
print('PG498_PENDING_NATIVE actual='+str(result.returncode)+' starts0=true epochUnchangedRequired=true diagnosticsPrivate=true')
raise SystemExit(result.returncode)
