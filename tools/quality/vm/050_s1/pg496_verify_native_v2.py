"""Fresh read-only PG496 verification, never invokes recover/start/stop/revoke.
Unknown completion must be reattached to the existing process, not replayed.
"""
import datetime,json,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
base=W/'pg496-verify-native-v2'
assert not base.with_suffix('.private.log').exists()
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
prefixes=['pg496-timeout-tools-v2','pg491-pending-tools-v1','pg490-migration-tools-v2','pg481-native-tools-v3','pg481-pending-tools-v1','pg480-backup-tools-v3','pg477-completed-tools-v1','pg477-partial-tools-v3','pg475-readback-tools-v1','pg474-readback-tools-v1','pg473-readback-tools-v1','pg471-readback-tools-v3','pg471-completed-tools-v2','pg469-current-tools-v3','pg468-recovery-tools-v4','pg468-recovery-tools-v2','pg466-tool-v3','pg465-completed-tool-v2','pg464-completed-readback-v7','pg464-code-tools-v2','pg461-known30-tool-v3','pg456-applied-tools-v7']
cp=':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)+':/opt/schubert-nk/releases/0.1.0-PG489/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG489/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG489/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG489/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
for suffix,value in [('.started',datetime.datetime.now(datetime.timezone.utc).isoformat()),('.operator-source',subprocess.check_output(['git','rev-parse','HEAD']).decode().strip())]:
 with pathlib.Path(str(base)+suffix).open('x') as f:f.write(value+'\n');f.flush();os.fsync(f.fileno())
with pathlib.Path(str(base)+'.private.log').open('xb') as f:
 for command in ['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg496TimeoutRecoveryTest',
  'sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 -B /var/lib/pgpt-s1-preservation/pg496-timeout-tools-v2/pg496_timeout_owned_test.py',
  'sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg496TimeoutRecovery verify']:
  result=subprocess.run(ssh+[command],stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  if result.returncode:break
for suffix,value in [('.exit',str(result.returncode)),('.completed',datetime.datetime.now(datetime.timezone.utc).isoformat())]:
 with pathlib.Path(str(base)+suffix).open('x') as f:f.write(value+'\n');f.flush();os.fsync(f.fileno())
print('PG496_NATIVE_VERIFY actual='+str(result.returncode)+' starts0=true stops0=true revoke0=true oldCloseNotInferred=true diagnosticsPrivate=true')
raise SystemExit(result.returncode)
