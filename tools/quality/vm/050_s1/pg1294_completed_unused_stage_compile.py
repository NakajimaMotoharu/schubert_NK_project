"""Freeze exact current-D5 ABI/owner and new769 signed archive; host only."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import tarfile
import pg1248_fresh_owned_stop_compile as previous
from pg1293_completed_unused_stage_sources import sources,SOURCE,DIGEST,BASELINE_SHA
from pg601_stage_contract import check_members

TARGET=previous.W/'pg1293-native-tools-v1'
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if json.loads((previous.W/'pg1287-current-readonly-v1.safe.json').read_bytes())['actualExit']!=0:
        raise ValueError('qualified current full post required')
    release=previous.W/'pg1292-release-v1';signature=P/'pg1292-manifest-v1.sig';bundle=P/'pg1295-release-v1.tar'
    record=json.loads((previous.W/'pg1292-candidate-build-v1.safe.json').read_bytes())
    if record['candidateSource']!=SOURCE or record['manifestSha256']!=DIGEST or not record['signatureVerified']:
        raise ValueError('new signed same-source candidate required')
    if hashlib.sha256(signature.read_bytes()).hexdigest()!=record['signatureSha256']or signature.stat().st_size!=64:
        raise ValueError('fixed actual candidate signature required')
    if os.path.lexists(TARGET)or os.path.lexists(bundle):raise ValueError('new-only compiler and archive required')
    if os.statvfs(P).f_bavail*os.statvfs(P).f_frsize<805306368:raise ValueError('preservation and close cushion required')
    raw=(release/'RELEASE-MANIFEST.json').read_bytes();data=json.loads(raw)
    if hashlib.sha256(raw).hexdigest()!=DIGEST or len(data['artifacts'])!=187:raise ValueError('fixed candidate manifest required')
    for row in data['artifacts']:
        path=release/row['path']
        if path.is_symlink()or path.stat().st_size!=row['size']or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('immutable candidate payload required')
    with tarfile.open(bundle,'x:')as archive:
        for path in sorted(release.rglob('*')):
            if path.is_symlink():raise ValueError('candidate link refused')
            archive.add(path,arcname=str(path.relative_to(release)),recursive=False)
    with tarfile.open(bundle,'r:')as archive:
        check_members(archive.getmembers(),{r['path']for r in data['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'})
    bundle_bytes=json.dumps({'archiveSha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'signatureSha256':record['signatureSha256']},sort_keys=True).encode()
    generated=sources()
    generated['pg1293_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle_bytes).hexdigest())+'\n'+generated['pg1293_native_refs.py']
    generated['bundle.safe.json']=bundle_bytes.decode()
    code=inspect.getsource(previous.main)
    for old,new in [('Pg1247NativeStop','Pg1293UnusedStage'),('Pg1247','Pg1293'),('pg1248','pg1294'),
      ('pg1217-frozen-v1.safe.json','pg1254-frozen-v1.safe.json'),("name.startswith('Pg1216')","name.startswith('Pg1253')"),
      ('pg1216-native-tools-v1','pg1253-native-tools-v1')]:
        if old not in code:raise ValueError('fixed current ABI compiler boundary required')
        code=code.replace(old,new)
    code=code.replace("'Pg1293StopLabelTest.java']]","'Pg1293StopLabelTest.java','Pg1293OriginalTupleTest.java']]")
    code=code.replace("('label','Pg1293StopLabelTest')","('label','Pg1293StopLabelTest'),('original','Pg1293OriginalTupleTest')")
    code=code.replace("'formalAccepted':False}","'formalAccepted':False,'candidateSource':CANDIDATE_SOURCE,'candidateManifestSha256':CANDIDATE_DIGEST,'bundleSha256':BUNDLE_SHA,'unusedPlacementOnly':True}")
    if 'Pg1293OriginalTupleTest.java'not in code:raise ValueError('independent actual original tuple fixture required')
    env=dict(previous.__dict__,TARGET=TARGET,sources=lambda:generated,BEFORE=BASELINE_SHA,
        CANDIDATE_SOURCE=SOURCE,CANDIDATE_DIGEST=DIGEST,BUNDLE_SHA=hashlib.sha256(bundle.read_bytes()).hexdigest())
    exec(compile(code,'<current genuine completed unused candidate compiler>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
