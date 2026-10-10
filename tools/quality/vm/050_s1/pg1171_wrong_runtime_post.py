"""Independent full post of typed wrongfile retirement; no prepare/start authority."""
import ast
import inspect
from pg1164_runtime_failed_owner_proof import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    s=previous();s=s[:s.index('JAVA=415524')]
    s=s.replace('runtime-failed-owner-proof-v1','wrong-runtime-post-v1')
    s=s.replace("reload_policy.configuration(CURRENT['configuration'],configuration,True)","reload_policy.configuration(CURRENT['configuration'],configuration,False)")
    s+=BODY;ast.parse(s);return s


BODY=r'''
COMPLETE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1166-runtime-retirement-v1')
fixed={'before.private.json':'2bb4a6c62da292691518a2d4a3b018df02e460639b9b4e044d843dd33b4b06c4',
 'prepared.private.json':'989635f8087b6c99dc950517566728b9a7a00cf37fed31d03451ac6089c88d70',
 'after.private.json':'989635f8087b6c99dc950517566728b9a7a00cf37fed31d03451ac6089c88d70',
 'complete.private':'6b0df270ac4002cae95838429e7b62647614cb9880b9b6959d1561073ac31ab4',
 'runtime-before.private':'d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0',
 'refs.private.err':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
for name,digest in fixed.items():require(hashlib.sha256((COMPLETE/name).read_bytes()).hexdigest()==digest)
expected=json.loads((COMPLETE/'after.private.json').read_bytes())
def post():
 v=capture();require(v['rows']==expected['rows']and v['units']==expected['units']and v['configuration']==expected['configuration'])
 for root,t in expected['trees'].items():require(tree(pathlib.Path(root))==t)
 runtime=tree(pathlib.Path('/run/systemd/system'));require(runtime==expected['runtime'])
 directory=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');require(not list(directory.iterdir())and md(directory)[2:6]==[0,0,stat.S_IFDIR|0o755,2])
 require(not pathlib.Path('/proc/415524').exists()and not pathlib.Path('/proc/415553').exists())
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=md(p);require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p));st=p.stat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and len(f[5].split(':'))==3:
    dev=f[5].split(':');require((int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino))
 resource_zero();v['runtime']=runtime;return v
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
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'wrongRuntimeRetired':True,'sameEmptyRuntimeDirectory755':True,'allOriginalRowsBackupNativeSourceUnchanged':True,'oldBad647BytesPrivatelyPreserved':True,'startupInvalidPreserved':True,'tenPhysicalHistoryRetained':True,'allPeersAdvisoryM_A0':True,'metadataReferencesNormalClose':True,'operationAuthority':False,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1171-wrong-runtime-post-v1').replace('PG1120-current-failed-capture-v1','PG1171-wrong-runtime-post-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<independent wrong runtime full post>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
