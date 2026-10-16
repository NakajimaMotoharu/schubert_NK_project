"""Read release names against its signed rows, without opening unsigned file contents or acting."""
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

BODY=r'''
import pathlib,json,hashlib
P=pathlib.Path
assert P('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
root=P('/opt/schubert-nk/current').resolve(strict=True);assert root==P('/opt/schubert-nk/releases/0.1.0-PG3976')
raw=(root/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
data=json.loads(raw);names={row['path']for row in data['artifacts']}|{'RELEASE-MANIFEST.json'}
expected_dirs={str(parent)for name in names for parent in pathlib.PurePosixPath(name).parents if str(parent)!='.'}
actual={str(p.relative_to(root)):('SYMLINK'if p.is_symlink()else'DIR'if p.is_dir()else'FILE')for p in root.rglob('*')}
extra={p:kind for p,kind in actual.items()if p not in names|expected_dirs}
print(json.dumps({'actualExit':0,'source':data['source']['commit'],'BOM':hashlib.sha256(raw).hexdigest(),'signedArtifacts':len(data['artifacts']),'additionalNames':extra,'missingSigned':sorted(names-set(actual)),'stateChangingActions':0}))
'''


def main():
    os.umask(0o077);out=W/'pg4142-signed-namespace-read-v1';out.mkdir()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
