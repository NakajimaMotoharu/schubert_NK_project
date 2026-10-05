"""PG467 synthetic initial ADMIN private provisioning. No DB writes or Unit starts.
Secrets are generated into new-only host private storage and sent by SSH stdin, never argv/log/Git.
"""
import json,os,pathlib,secrets,subprocess,sys
require=lambda b: b or (_ for _ in ()).throw(ValueError('fixed private provisioning refused'))
require(len(sys.argv)==1)
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
LOCAL=PRIVATE/'pg467-bootstrap-account.private.json'
require(not LOCAL.exists() and PRIVATE.stat().st_uid==os.getuid() and PRIVATE.stat().st_mode&0o077==0)
value={'username':'pgpt_admin_467','password':secrets.token_urlsafe(32)}
fd=os.open(LOCAL,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:json.dump(value,stream);stream.flush();os.fsync(stream.fileno())
PAYLOAD=r'''import hashlib,json,os,pathlib,stat,subprocess,sys
def require(b):
 if not b:raise ValueError('fixed private provisioning refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54')
current=pathlib.Path('/opt/schubert-nk/current');require(current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG465'))
require(hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e')
require(b'newOwnedScopesReturnedNormally=true' in pathlib.Path('/var/lib/pgpt-s1-preservation/pg466-completed-recovery/complete.private').read_bytes())
raw=sys.stdin.buffer.read(4097);require(len(raw)<=4096);value=json.loads(raw);require(set(value)=={'username','password'} and value['username']=='pgpt_admin_467' and isinstance(value['password'],str) and 12<=len(value['password'])<=128 and value['password'].isascii())
require(subprocess.check_output(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c','select count(*) from schubert.app_users'],timeout=5).strip()==b'0')
require(subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-bootstrap-admin.service','--property=ActiveState,MainPID,ControlPID,Job'],text=True,timeout=5).splitlines()==['ActiveState=inactive','Job=','MainPID=0','ControlPID=0'])
root=pathlib.Path('/etc/schubert-nk/credentials');st=root.lstat();require(stat.S_ISDIR(st.st_mode) and st.st_uid==0 and st.st_mode&0o022==0)
paths=[root/'bootstrap-admin-username',root/'bootstrap-admin-password'];require(all(not p.exists() and not p.is_symlink() for p in paths))
for name,p in zip(('username','password'),paths):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400)
 with os.fdopen(fd,'wb') as f:f.write(value[name].encode('ascii'));f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG467_BOOTSTRAP_PRIVATE_PROVISIONED credentialCount2=true private400=true dbWrites0=true starts0=true secretsPrinted=false')
'''
ssh=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
result=subprocess.run(ssh+['sudo -n /usr/bin/python3 -B -c '+__import__('shlex').quote(PAYLOAD)],input=json.dumps(value).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print('PG467_BOOTSTRAP_PROVISION actualExit='+str(result.returncode)+' localPrivateRetained=true secretsPrinted=false')
if result.returncode==0:require(result.stdout==b'PG467_BOOTSTRAP_PRIVATE_PROVISIONED credentialCount2=true private400=true dbWrites0=true starts0=true secretsPrinted=false\n')
else:print('PG467_BOOTSTRAP_PROVISION_REFUSED noRetryWithoutCurrentReadback=true')
raise SystemExit(result.returncode)
