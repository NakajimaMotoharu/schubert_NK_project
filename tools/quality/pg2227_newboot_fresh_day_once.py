"""One separately qualified genuine new-day normal Root, never old run replay.

PT-OPS-2227-001. No operator INVALID, resume, Backup/ADMIN reissue or Unit change.
"""
import json
import hashlib
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1456_current_day_once import BODY
from pg2226_newboot_fresh_day_before import payload as before_payload
from pg2224_newboot_current_observer import namespace
from pg2208_current_newboot_cold_sources import bindings,BOOT
from pg2176_newsource_normal_observer import SOURCE,BOM

SLOT='pg2227-newboot-fresh-day-once-v1'


def compose(before_sha,watch_files):
    if type(before_sha)is not str or len(before_sha)!=64 or any(c not in '0123456789abcdef'for c in before_sha):raise ValueError('one actual current before hash required')
    expected={'pg2224_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}
    if type(watch_files)is not dict or set(watch_files)!=expected:raise ValueError('whole immutable current observer closure required')
    raw=before_payload().split('bus=dbus.SystemBus',1)[0]
    marker="SAVE=BASE/'pg2226-newboot-fresh-day-before-v1';SAVE.mkdir(mode=0o700)"
    if raw.count(marker)!=1:raise ValueError('one exact independent before boundary required')
    raw=raw.replace(marker,"SAVE=BASE/"+repr(SLOT)+";require(not os.path.lexists(SAVE))")
    body=bindings(BODY).replace('pg1454','pg2224').replace('pg1455-current-day-before-v1','pg2226-newboot-fresh-day-before-v1').replace('pg1456-current-day-once-v1',SLOT).replace('PG1456-current-day-once-v1','PG2227-newboot-fresh-day-once-v1')
    body=body.replace('>=805306368','>=12884901888')
    raw+='\nBEFORE_SHA='+repr(before_sha)+'\nWATCH_FILES='+repr(watch_files)+'\n'+body
    if check(raw,'<actual newboot normal fresh-day once closure>'):raise ValueError('whole actual exports required')
    compile(raw,'<newboot separate fresh-day once>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean source required')
    value=json.loads((W/'pg2226-newboot-fresh-day-before-v1/manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['guest']['existingSuccessfulInspectorStepsForDate']!=0:raise ValueError('actual independent new-day before required')
    if not(W/'pg2224-watch-v1.started').exists()or(W/'pg2224-watch-v1.exit').exists():raise ValueError('live current immutable observer required')
    files={n:hashlib.sha256(s.encode()).hexdigest()for n,s in namespace()['files']().items()}
    actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2224-observer-stage-v1').iterdir()}
    if actual!=files:raise ValueError('unchanged actual observer files required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=compose(value['guest']['privateBeforeSha256'],files).encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,stdout=f,stderr=f,timeout=90)
    safe={'actualExit':r.returncode,'productionSource':SOURCE,'bom':BOM,'boot':BOOT,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True}
    if not r.returncode:safe['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps(safe));return r.returncode


if __name__=='__main__':raise SystemExit(main())
