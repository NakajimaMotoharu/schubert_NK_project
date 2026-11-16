"""Freeze only public characterization source and eight pinned SDK jars for ordinary124."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tarfile

r=Path.cwd();w=r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1';assert not w.exists();w.mkdir(mode=0o700)
b=r/'evidence/01_PT/018_NK-OPS-001';audit=json.loads((b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json').read_text());tc=r.parent/'toolchain'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=audit['actualUnitSource'];assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==source
assert subprocess.run(['git','diff','--exit-code',source,'--','program/characterization'],stdout=subprocess.DEVNULL).returncode==0
with (w/'snapshot.tar').open('xb') as f:subprocess.run(['git','archive','--format=tar',source,'program/characterization'],stdout=f,check=True)
snap=w/'unpack';snap.mkdir()
with tarfile.open(w/'snapshot.tar') as t:t.extractall(snap,filter='data')
inputs={str(p.relative_to(snap)):sha(p) for p in sorted(snap.rglob('*')) if p.is_file()}
assert all(inputs[path]==h for path,h in audit['sourceRootBaselineHashes'].items())
jarpaths=[tc/'junit-platform-console-standalone-1.13.4.jar',tc/'org.jacoco.cli-0.8.15-nodeps.jar',tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar',tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',*[tc/'m2/repository/com/fasterxml/jackson/core'/name/version/(name+'-'+version+'.jar') for name,version in [('jackson-annotations','2.19.2'),('jackson-core','2.19.2'),('jackson-databind','2.19.2')]],tc/'m2/repository/com/microsoft/playwright/playwright/1.55.0/playwright-1.55.0.jar']
sdk=w/'sdk';sdk.mkdir()
for p in jarpaths:assert p.is_file();shutil.copyfile(p,sdk/p.name)
assert len(list(sdk.iterdir()))==8
runner=b/'input/4555_p020_remote_whole124.py';shutil.copyfile(runner,w/'runner.py')
cfg=dict(source=source,sourceCore=audit['sourceCore'],archiveSha256=sha(w/'snapshot.tar'),sourceHashes=inputs,sdkHashes={p.name:sha(p) for p in sorted(sdk.iterdir())},compileSdk=[p.name for p in jarpaths if 'jacoco' not in p.name],selectedSuites=[x['suite'] for x in audit['selectedWholeSuites']],expectedInvocations=124,runnerSha256=sha(runner),scopeAuditSha256=sha(b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json'),remoteSlot='/home/mini/schubert-nk-pgpt/wbs66-p020-20261117-pg37012',realVmServiceNativeDbActions=0)
(w/'package.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
with tarfile.open(w/'public-package.tar','x') as t:
 for name in ['snapshot.tar','sdk','runner.py','package.json']:t.add(w/name,arcname=name)
manifest=dict(actualExit=0,source=source,sourceCore=audit['sourceCore'],archiveSha256=cfg['archiveSha256'],packageSha256=sha(w/'public-package.tar'),packageBytes=(w/'public-package.tar').stat().st_size,sdkHashes=cfg['sdkHashes'],sourceHashes=inputs,runnerSha256=cfg['runnerSha256'],selectedSuites=cfg['selectedSuites'],expectedInvocations=124)
out=b/'evidence/PG37008-p020-public-package-v1';out.mkdir();(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,source=source,main5=True,wholeSuites=17,expected=124,sdkJars=8,packageBytes=manifest['packageBytes'],packageSha256=manifest['packageSha256'])))
