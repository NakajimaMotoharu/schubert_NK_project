"""Independent completed verify-only join, all original full values retained."""
import ast
import inspect
from pg1177_canonical_runtime_owner_proof import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    s = previous();s = s[:s.index('JAVA=420139')]
    s = s.replace('canonical-runtime-owner-proof-v1', 'canonical-runtime-post-v1')
    s += BODY;ast.parse(s);return s


BODY = r'''
COMPLETE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1179-runtime-verify-v1')
fixed={'before.private.json':'3e1e7d324d95c493ba24429f7cd1abc81c996566b99ac0ce40f46b61236d3325',
 'prepared.private.json':'3e1e7d324d95c493ba24429f7cd1abc81c996566b99ac0ce40f46b61236d3325',
 'after.private.json':'3e1e7d324d95c493ba24429f7cd1abc81c996566b99ac0ce40f46b61236d3325',
 'complete.private':'b341bb8f210cab1e5e688b20e445c477ea81410efdc73c521d151072aaf61073',
 'new-runtime.private':'d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0',
 'refs.private.err':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
for name,digest in fixed.items():require(hashlib.sha256((COMPLETE/name).read_bytes()).hexdigest()==digest)
expected=json.loads((COMPLETE/'after.private.json').read_bytes())
prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/canonical-runtime-owner-handoff-v1/after.private.json')
raw=prior.read_bytes();require(hashlib.sha256(raw).hexdigest()=='d218c5e294937078d6535b1871552a2bac1f4a3a81c8a46f47f0f018b79b8550');prior=json.loads(raw)
def post():
 v=capture();v['runtime']=tree(pathlib.Path('/run/systemd/system'));require(v==prior)
 require(v['rows']==expected['rows']and v['units']==expected['units']and v['configuration']==expected['configuration']and v['runtime']==expected['runtime'])
 for root,values in expected['trees'].items():require(tree(pathlib.Path(root))==values)
 require(all(not pathlib.Path('/proc',str(p)).exists()for p in [420139,420168]))
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=md(p);require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p));st=p.stat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and len(f[5].split(':'))==3:
    dev=f[5].split(':');require((int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino))
 resource_zero();return v
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
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'canonicalRuntimeVerified':True,'sameActiveRunCutoffActivation':True,'allOriginalRowsBackupNativeSourceUnchanged':True,'startupInvalidPreserved':True,'tenPhysicalHistoryRetained':True,'allPeersAdvisoryM_A0':True,'metadataReferencesNormalClose':True,'configurationWritesReloadStarts0':True,'operationAuthority':False,'formalAccepted':False}))
'''


def main():
    s = inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1', 'pg1182-canonical-runtime-post-v1').replace('PG1120-current-failed-capture-v1', 'PG1182-canonical-runtime-post-v1')
    env = dict(transport.__dict__);env['PAYLOAD'] = payload()
    exec(compile(s, '<independent canonical runtime post>', 'exec'), env);return env['main']()


if __name__ == '__main__':raise SystemExit(main())
