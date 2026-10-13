"""Independent recovered whole post; exact partial file retained, reload still absent."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
from pg2322_current_partial_runtime_pair_proof import body,SOURCE

SLOT='pg2326-current-partial-runtime-recovery-post-v1'


TAIL=r'''
require(not any(pathlib.Path('/proc',str(pid)).exists()for pid in [98485,98516,98514]))
for name in ['maintenance.lock','startup-admission.lock']:
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  words=line.split()
  if len(words)<8:continue
  value=words[5].split(':')
  require(len(value)!=3 or(int(value[0],16),int(value[1],16),int(value[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
saved=(base/'pg2322-current-partial-runtime-pair-proof-v1/proof.private.json').read_bytes()
require(hashlib.sha256(saved).hexdigest()=='4385ba0ed4594081e3549d4ae03eb5b3678042d4ab72bd7e319a81501b928f3b')
old_names=json.loads(saved)['pair']['child']['busNames']
bus=dbus.SystemBus(private=True)
try:
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(name)for name in old_names))
finally:bus.close()
save=base/'pg2326-current-partial-runtime-recovery-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'before':after,'native':native,'all24And32And187Unchanged':True,'allClientAdvisoryFlock0':True,'oldPairGone':True,'oldBusGone':True,'exactPartialRuntimeRetained':True,'reloadNotReserved':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'afterSha256':hashlib.sha256(encoded).hexdigest(),'all24And32And187Unchanged':True,'allClientAdvisoryFlock0':True,'oldPairGone':True,'oldBusGone':True,'exactPartialRuntimeRetained':True,'reloadNotReserved':True,'oldCloseUnknown':True,'formalAccepted':False}))
'''


def payload():
    raw=body().replace('PEER_CLOSED=False','PEER_CLOSED=True')+TAIL
    if check(raw,'<whole partial recovery independentpost>'):raise ValueError('all recoverypost globals required')
    compile(raw,'<whole current partial runtime post>','exec');return raw


def main():
    value=json.loads((W/'pg2324-current-partial-runtime-handoff-v1/manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['stages'][-1].get('ownedActorsDBAdvisoryFlockAndBusGone')is not True:raise ValueError('actual current pair recovery required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not result.returncode:value['guest']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
