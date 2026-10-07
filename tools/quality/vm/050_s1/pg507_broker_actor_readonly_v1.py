"""Single passive actor projection probe, no parent attachment or JMS/DB mutation."""
import hashlib,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
raw=(W/'pg507-broker-readonly-tools-v1/Pg507BrokerActorReadonly.class').read_bytes()
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
log=W/'pg507-broker-actor-readonly-v1.private.log';assert not log.exists()
payload=r'''
import hashlib,pathlib,os,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
p=pathlib.Path('/home/ubuntu/pg507-broker-readonly-v1.class');assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg507-broker-readonly-v1');assert not r.exists();r.mkdir(mode=0o700)
with (r/'Pg507BrokerActorReadonly.class').open('xb') as f:os.fchmod(f.fileno(),0o400);f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
cp=str(r)+':/opt/schubert-nk/releases/0.1.0-PG495/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG495/api/lib/*:/opt/schubert-nk/releases/0.1.0-PG495/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG495/operations/lib/*'
result=subprocess.run(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg507BrokerActorReadonly']);raise SystemExit(result.returncode)
'''
with log.open('xb') as f:
 result=subprocess.run(ssh+['sudo -n python3 -B -'],input=('SHA='+repr(hashlib.sha256(raw).hexdigest())+'\n'+payload).encode(),stdout=f,stderr=f)
with (W/'pg507-broker-actor-readonly-v1.exit').open('x') as f:f.write(str(result.returncode)+'\n')
print('PG507_READONLY exit='+str(result.returncode)+' privateLogSha256='+hashlib.sha256(log.read_bytes()).hexdigest()+' parentActions0=true')
raise SystemExit(result.returncode)
