"""Fresh existing primary VM/forward/BOM187 read-only identity, never an admission or restart."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from lan_server import run
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

ROOT = Path(__file__).resolve().parents[2]

HOST = """python3 - <<'HOST'
from pathlib import Path
import json,hashlib
p=Path('/proc/4599');assert p.is_dir();argv=(p/'cmdline').read_bytes();ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19]);boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert ticks==101242 and hashlib.sha256(argv).hexdigest()=='f765c39c924d24fc03739355785e22c06b302d68418a85860e3d661960a2b106'
assert b'/home/mini/schubert-nk-pgpt/vm/pg2810-network-resume-cold-v1/active.qcow2'in argv
print(json.dumps({'pid':4599,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'boot':boot,'dedicatedActiveDisk':True}))
HOST"""

GUEST = r'''
from pathlib import Path
import json,hashlib,os,subprocess,datetime
assert os.geteuid()==0
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert boot=='79a3260a-e16d-42bf-942a-b914ed144c28'
assert Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
current=Path('/opt/schubert-nk/current');root=current.resolve(strict=True);manifest=root/'RELEASE-MANIFEST.json';raw=manifest.read_bytes();sha=hashlib.sha256(raw).hexdigest();data=json.loads(raw)
assert sha=='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'
assert data['source']['commit']=='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'and data['release']=='0.1.0-PG2802'and data['versions']['schema']=='028'
rows=data['artifacts'];assert len(rows)==187 and len({r['path']for r in rows})==187
for row in rows:
 p=root/row['path'];assert p.resolve().is_relative_to(root)and not p.is_symlink()and p.is_file()
 assert p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
pin=Path('/etc/schubert-nk/deployment-key/pin.der');signature=Path('/var/lib/pgpt-s1-preservation/pg2802-manifest.sig');assert pin.stat().st_size==44 and signature.stat().st_size==64
verified=subprocess.run(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(pin),'-in',str(manifest),'-sigfile',str(signature)],capture_output=True,timeout=10);assert verified.returncode==0
units={}
names=['schubert-nk-'+name+'.service'for name in ['morning','api','web','backup','cleanup','expiry-cleanup','inbox-inspector']]+['caddy.service','artemis.service']
for name in names:
 r=subprocess.run(['/usr/bin/systemctl','show',name,'--no-pager','-p','LoadState','-p','ActiveState','-p','SubState','-p','MainPID','-p','Job','-p','InvocationID'],capture_output=True,text=True,timeout=10);assert r.returncode==0
 item=dict(line.split('=',1)for line in r.stdout.splitlines()if'='in line)
 invocation=item.pop('InvocationID','');item['invocationSha256']=hashlib.sha256(invocation.encode()).hexdigest();units[name]=item
assert current.resolve(strict=True)==root and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guestBoot':boot,'deployedSource':data['source']['commit'],'release':data['release'],'bomSha256':sha,'artifactsVerified':187,'signatureVerifyExit':0,'signatureSha256':hashlib.sha256(signature.read_bytes()).hexdigest(),'pinSha256':hashlib.sha256(pin.read_bytes()).hexdigest(),'units':units,'vmActions':0,'unitActions':0,'dbClaims':False,'admissionAuthorityIssued':False,'oldNativeTransferred':False}))
'''


def main():
    os.umask(0o077); out = W / 'pg3428-primary-readonly-v1'; out.mkdir()
    local = Path('/proc/20445'); assert local.is_dir()
    forward = {'pid': 20445, 'ticks': int((local / 'stat').read_text().rsplit(')', 1)[1].split()[19]),
               'argvSha256': hashlib.sha256((local / 'cmdline').read_bytes()).hexdigest()}
    assert forward == {'pid': 20445, 'ticks': 104194, 'argvSha256': 'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}
    code, text = run(HOST, timeout=30); assert code == 0
    host = json.loads(text.strip()); (out / 'guest-readonly.private.py').write_text(GUEST)
    with management_gate(P / 'current-management-critical.lock'):
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=GUEST.encode(), capture_output=True, timeout=150)
    (out / 'observer.private.log').write_bytes(actual.stdout + actual.stderr)
    assert actual.returncode == 0, 'fresh read-only VM identity not established; no state-changing fallback'
    result = json.loads(actual.stdout); result.update(host=host, localForward=forward, payloadSha256=hashlib.sha256(GUEST.encode()).hexdigest(), candidateDeployed=False)
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3428-primary-readonly'; public.mkdir()
    path = public / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'deployedSource': result['deployedSource'], 'artifactsVerified': 187,
                      'signatureVerifyExit': 0, 'guestBoot': result['guestBoot'], 'units': result['units'],
                      'stateChangingActions': 0, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
