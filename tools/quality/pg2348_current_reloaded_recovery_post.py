"""Independent whole post after SSC284 pair recovery; never repeat reload."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
from pg2338_current_reloaded_pair_proof import body,declared_configuration,SOURCE

SLOT='pg2348-current-reloaded-recovery-post-v1'


TAIL=r'''
require(not any(pathlib.Path('/proc',str(pid)).exists()for pid in [101019,101050,101048]))
for name in ['maintenance.lock','startup-admission.lock']:
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  words=line.split()
  if len(words)<8:continue
  value=words[5].split(':')
  require(len(value)!=3 or(int(value[0],16),int(value[1],16),int(value[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
failed=base/'pg2334-current-existing-runtime-finish-v1'
require({p.name for p in failed.iterdir()}=={'before.private.json','daemon-reload-reserved.private','refs-prepare.private.log'})
require(hashlib.sha256((failed/'before.private.json').read_bytes()).hexdigest()=='cabdde419263ccf365c32c773df9e028f1e7fb4b69f8ed51b21fd5073755d79e')
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='e34d11d01de4317f7ab9f72895eae56ceffa5f5aee9c6419d1eba7196edd08b1')
require((failed/'daemon-reload-reserved.private').read_bytes()==b'one normal existing-runtime daemon-reload; no retry\n')
saved=(base/'pg2342-current-reloaded-pair-proof-v2/proof.private.json').read_bytes()
require(hashlib.sha256(saved).hexdigest()=='a8eb610cff840dc9be93eb83f59d369097ec145d743c92e62d1e5344a41147ff')
old_names=json.loads(saved)['pair']['child']['busNames']
bus=dbus.SystemBus(private=True)
try:
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(name)for name in old_names))
finally:bus.close()
save=base/'pg2348-current-reloaded-recovery-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'before':{**after,'configuration':dict(current_view)},'native':native,'all24And187Unchanged':True,'configurationDeclaredDeltaAndClosedOnly':True,'state18Unchanged':True,'allClientAdvisoryFlock0':True,'oldPairGone':True,'oldBusGone':True,'exactRuntimeRetained':True,'oldCloseUnknown':True,'verificationOnlyNormalScopePending':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'afterSha256':hashlib.sha256(encoded).hexdigest(),'all24And187Unchanged':True,'configurationDeclaredDeltaAndClosedOnly':True,'state18Unchanged':True,'allClientAdvisoryFlock0':True,'oldPairGone':True,'oldBusGone':True,'exactRuntimeRetained':True,'oldCloseUnknown':True,'verificationOnlyNormalScopePending':True,'formalAccepted':False}))
'''


def payload():
    raw=body().replace('PEER_CLOSED=False','PEER_CLOSED=True')+TAIL
    if check(raw,'<whole current reloaded recovery post>'):raise ValueError('all reloadedpost globals required')
    compile(raw,'<whole independent reloaded post>','exec');return raw


def main():
    old=json.loads((W/'pg2346-current-eleven-fd-handoff-v2/manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or not old['stages'][-1]['ownedActorsDBAdvisoryFlockAndBusGone']:raise ValueError('current owned pair gone required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not result.returncode:value['guest']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
