"""Off-server age decryption; plaintext/catalog hashes remain private and never printed."""
import hashlib,io,json,os,pathlib,subprocess,tarfile
os.umask(0o077)
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
NAMES=('db-api','db-web','db-batch','db-migration','backup-pgpass','mq-api','mq-web','mq-maintenance','mq-ops','api-context-aes-current','api-inbox-response-aes-current','operation-hmac-current','web-session-aes-current','web-revoke-aes-current','web-log-aes-current','artemis-users','db-inbox-inspector')
age='/home/mini/codex/project1/work/toolchain/age-1.2.1/root/usr/bin/age';keygen='/home/mini/codex/project1/work/toolchain/age-1.2.1/root/usr/bin/age-keygen'
assert (W/'pg563-backup-capture-v1.exit').read_bytes()==b'0\n'
target=W/'pg563-host-credential-verify-v1';assert not target.exists();target.mkdir(mode=0o700)
with tarfile.open(P/'pg563-current-backup-v1.private.tar')as bundle:
 members=bundle.getmembers();assert len(members)==4 and {m.name for m in members}=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'}and all(m.isfile()for m in members)
 manifest=json.loads(bundle.extractfile('MANIFEST.json').read());cipher=bundle.extractfile('credentials.tar.age').read()
public=subprocess.run([keygen,'-y',str(P/'pg381-backup-age.key')],capture_output=True);assert public.returncode==0 and hashlib.sha256(public.stdout).hexdigest()==manifest['recipientSha256']
decryption=subprocess.run([age,'-d','-i',str(P/'pg381-backup-age.key')],input=cipher,capture_output=True);assert decryption.returncode==0 and 0<len(decryption.stdout)<=16777216
with tarfile.open(fileobj=io.BytesIO(decryption.stdout))as archive:
 members=archive.getmembers();assert len(members)==17 and {m.name for m in members}==set(NAMES)
 assert all(m.isfile()and not m.issym()and not m.islnk()and m.uid==0 and m.mode==0o600 for m in members)
 actual={m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest()for m in members}
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
payload='NAMES='+repr(NAMES)+'\n'+'''import hashlib,json,pathlib,os,stat
root=pathlib.Path('/etc/schubert-nk/credentials');result={}
for name in NAMES:
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and 0<s.st_size<=1048576
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb')as f:raw=f.read()
 assert p.lstat()==s;result[name]=hashlib.sha256(raw).hexdigest()
print(json.dumps(result))
'''
result=subprocess.run(ssh,input=payload.encode(),capture_output=True);assert result.returncode==0
with (target/'catalog.private.json').open('xb')as f:f.write(result.stdout);f.flush();os.fsync(f.fileno())
assert actual==json.loads(result.stdout)
safe={'id':'PG563-offserver-credential-verification-v1','actualExit':0,'ageDecryption0':True,'recipientPublicFingerprintVerified':True,'credentialCatalogCount':17,'allCatalogEntriesRegularRoot600':True,'allCredentialBytesEqualCurrentSources':True,'privateKeyNeverOnServer':True,'credentialNamesPermissionsValuesNotExported':True,'rawExported':False,'ITSTAccepted':False,'plaintextPersisted':False}
with (target/'result.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(safe))
