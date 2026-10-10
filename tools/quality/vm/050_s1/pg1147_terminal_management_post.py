"""Independent full read-only post of fresh management, no native mutation."""
import ast
import inspect
from pg1141_failed_owner_preflight import payload as previous
import pg1120_current_failed_capture as transport

COMPLETE='/var/lib/pgpt-s1-preservation/pg1144-terminal-recovery-v1'


def payload():
    raw=previous().replace('failed-owner-preflight-v1','terminal-management-post-v1')
    marker='def tick(pid):return'
    raw=raw[:raw.index(marker)]+BODY
    old="dependent.whole(FAILED['units'],us,deps,cleanup_active=True)"
    new="expected_old={u:dict(v)for u,v in FAILED['units'].items()};expected_old['schubert-nk-cleanup.service'].update(ActiveState='inactive',SubState='dead');dependent.whole(expected_old,us,deps)"
    if raw.count(old)!=1:raise ValueError('fixed remaining Cleanup terminal projection refused')
    raw=raw.replace(old,new)
    old="require({p.name for p in startup.iterdir()}=={'epoch.current',epoch+'.owner',epoch+'.permit',epoch+'.API.start.intent'})"
    new="require({p.name for p in startup.iterdir()}=={'epoch.current',epoch+'.owner',epoch+'.permit'});require((startup/'epoch.current').read_bytes()==INVALID)"
    if raw.count(old)!=1:raise ValueError('fixed canonical invalid post insertion refused')
    raw=raw.replace(old,new)
    raw='INVALID='+repr(INVALID)+'\n'+raw
    ast.parse(raw);return raw


INVALID=(b'NKEPOCH1\nstate=INVALID\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\n'
         b'epoch_id=ecf22224-112b-46b5-a103-bde3aab63229\nrun_id=343a5a1b-d064-47d5-88c2-31c36d7ba7a4\n'
         b'cutoff_utc=2026-10-10T12:40:27.396847Z\nactivation_id=ada3f7ff-8287-48d7-9ba9-5cce71f61bd3\npermit_sha256=-\n')

BODY=r'''
COMPLETE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1144-terminal-recovery-v1')
fixed={'before.private.json':'bfed3114ab96ae5c638479ed74fbb5edae2cdef925f5616293c18ef17f00d772',
       'after.private.json':'85d86f84d2ec7877708f32a0027827a4a2b33d96a717e1cf76fc085cbb3af418',
       'retired.private.json':'85d86f84d2ec7877708f32a0027827a4a2b33d96a717e1cf76fc085cbb3af418',
       'complete.private':'532a654b1fe49a61177732be3a5beb1b7b231ed752afc3c092c5b491129b1c6c',
       'cleanup-manager.private.jsonl':'fd1a01b3b7f5a52527f3dd9102b703b87b0ddf3840cd86bebf7d6d21bb5c54aa',
       'schubert-nk-cleanup.service.stopped.private':'7dd7282f08c9dc2cf08b19d93320ce672f972c79d0fbb1ef90bebd06809702f1'}
for name,digest in fixed.items():
 p=COMPLETE/name;require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
root=pathlib.Path('/run/schubert-nk/startup')
expected_startup={'epoch.current':(264,'b54c6d46594575e9c46f3d2e46e8a282f657bfeca6f194a38060f3533684e72d'),
 'ecf22224-112b-46b5-a103-bde3aab63229.owner':(409,'51382b74bc2886f0bc6f1be1deba6256ff1456015940c7f6286e37e0997afd70'),
 'ecf22224-112b-46b5-a103-bde3aab63229.permit':(700,'713a1a2895e1f5804c477edf2032cf57ff7f6c4ce3369a4ed7cb2bdd9df4107a')}
expected=json.loads((COMPLETE/'after.private.json').read_bytes())
def post():
 value=capture();require(value['rows']==expected['rows'])
 for name,tree_before in expected['trees'].items():require(tree(pathlib.Path(name))==tree_before)
 for name,(size,digest)in expected_startup.items():
  p=root/name;m=md(p);require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,size]and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 for pid in [404585,404614,253968]:require(not pathlib.Path('/proc',str(pid)).exists())
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=md(p);require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p));s=p.stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   v=row.split()
   if len(v)>=8 and len(v[5].split(':'))==3:
    d=v[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 resource_zero();return value
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 observed=post();require(observed==post());SAVE.mkdir(mode=0o700)
 with(SAVE/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(observed,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 require(observed==post())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'tenPhysicalTerminal':True,'allRowsOriginalsBackupSourceUnchanged':True,'canonicalInvalidThreeFilesVerified':True,'oldPermitOwnerPreserved':True,'singleApiIntentRetired':True,'allPeersAdvisoryMaintenanceAdmission0':True,'metadataReferencesNormalClose':True,'operationAuthority':False,'formalAccepted':False}))
'''


def main():
    text=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1147-terminal-management-post-v1').replace('PG1120-current-failed-capture-v1','PG1147-terminal-management-post-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(text,'<fresh independent terminal post>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
