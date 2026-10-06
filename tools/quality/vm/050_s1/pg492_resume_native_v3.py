"""One owned runtime preparation; unknown delivery requires reattachment, not replay."""
import datetime,hashlib,json,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='38899a05b5c2daeecfc5af8ea5ae748e29954c60'
DIGEST='652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c'
assert (W/'pg489-six-full-v2.source').read_text().strip()==SOURCE
assert (W/'pg489-six-full-v2.exit').read_text().strip()=='0'
log=W/'pg492-resume-native-v3.private.log';assert not log.exists()
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
prefixes=['pg492-resume-tools-v3','pg491-pending-tools-v1','pg490-migration-tools-v2','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG489/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG489/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG489/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG489/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
with log.open('xb') as f:
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush();os.fsync(f.fileno())
 test=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg492ResumePreparationTest'],stdout=f,stderr=f);assert test.returncode==0
 result=subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg492ResumePreparation '+SOURCE+' '+DIGEST],stdout=f,stderr=f)
 f.write((datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n').encode());f.flush();os.fsync(f.fileno())
with (W/'pg492-resume-native-v3.exit').open('x') as f:f.write(str(result.returncode)+'\n')
print('PG492_RESUME_NATIVE actual='+str(result.returncode)+' parentStart0=true oldCloseNotInferred=true diagnosticsPrivate=true')
raise SystemExit(result.returncode)
