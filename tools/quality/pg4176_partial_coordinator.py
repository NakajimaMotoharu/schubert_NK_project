"""New-only SSC288 stage/proof under authenticated retained host gate. Recover not exposed yet."""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1724_retained_host_gate import queued_gate
import pg4168_retained_pair_keeper as keeper
import pg4166_partial_recovery_sources as partial

SLOT='pg4176-partial-tools-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+SLOT


def owner(path):
    proc=Path('/proc/595379');fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
    if int(fields[19])!=14277246 or hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()!='7bfafc9766fc7469583dd5e760d92c745ef1e14708f53706bfce601b0c003248':
        raise ValueError('same original observer required')
    s=path.lstat()
    if not(stat.S_ISREG(s.st_mode)and s.st_uid==os.geteuid()and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(path)):
        raise ValueError('same private gate envelope required')
    matching=[f for f in(proc/'fd').iterdir()if str(f.readlink())==str(path)]
    if len(matching)!=1 or (matching[0].stat().st_dev,matching[0].stat().st_ino)!=(s.st_dev,s.st_ino):raise ValueError('original gate descriptor required')
    rows=[line.split()for line in Path('/proc/locks').read_text().splitlines()if len(line.split())>=8 and line.split()[5]==f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}']
    if len(rows)!=1 or rows[0][1:5]!=['FLOCK','ADVISORY','WRITE','595379']:raise ValueError('sole original host exclusion required')
    return True


def files():return {'keeper.py':keeper.payload(),'partial.py':partial.controller(),'post.py':partial.post()}


def stage_payload():
    values=files()
    if any(check(text,'<'+name+'>')for name,text in values.items()):raise ValueError('all three full payloads static0 first')
    return 'FILES='+repr({n:base64.b64encode(t.encode()).decode()for n,t in values.items()})+'\nROOT='+repr(GUEST)+'\n'+r'''
from pathlib import Path
import base64,hashlib,json,os
assert os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
assert Path('/opt/schubert-nk/current').resolve(strict=True)==Path('/opt/schubert-nk/releases/0.1.0-PG3976')
assert hashlib.sha256(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
os.umask(0o077);root=Path(ROOT);root.mkdir(mode=0o700);hashes={}
for name,encoded in FILES.items():
 raw=base64.b64decode(encoded);compile(raw,'<fixed staged '+name+'>','exec');p=root/name
 with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 p.chmod(0o400);assert not os.listxattr(p)and p.lstat().st_nlink==1;hashes[name]=hashlib.sha256(raw).hexdigest();assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[name]
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','files':hashes,'stateChangingBusinessActions':0}))
'''


def main():
    if sys.argv[1:]not in (['stage'],['proof']):raise SystemExit('stage or proof only; owned TERM disabled before design qualification')
    action=sys.argv[1];os.umask(0o077);out=W/(SLOT+'-'+action);out.mkdir()
    owner(P/'current-management-critical.lock')
    with queued_gate(P/'current-management-critical.lock',validate_owner=owner,require_completion=lambda:False):
        if action=='stage':
            raw=stage_payload();(out/'payload.private.py').write_text(raw)
            r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=60)
        else:
            qualified=json.loads((W/(SLOT+'-stage')/'manifest.safe.json').read_bytes())
            if qualified['actualExit']!=0:raise ValueError('original staged artifacts first')
            expected={n:hashlib.sha256(t.encode()).hexdigest()for n,t in files().items()}
            if qualified['result']['files']!=expected:raise ValueError('staged artifact unchanged')
            r=subprocess.run(SSH+['sudo','-n','python3','-B',GUEST+'/keeper.py','proof'],capture_output=True,timeout=240)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.safe.json').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','action':action,'signalsIssued':0,'old4152Normal':False}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
