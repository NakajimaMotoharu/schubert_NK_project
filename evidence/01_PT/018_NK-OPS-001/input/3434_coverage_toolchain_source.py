"""Install pinned pure-Python coverage wheel outside Git, with official source/hash record."""
from pathlib import Path, PurePosixPath
import datetime,hashlib,json,urllib.request,zipfile
r=Path.cwd();out=r.parent/'toolchain/coverage-7.17.3';e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG33720-end-checkpoint-input-tool-v1';assert not out.exists() and not e.exists();e.mkdir()
url='https://pypi.org/pypi/coverage/7.17.3/json'
with urllib.request.urlopen(url,timeout=30) as f:metadata=json.load(f)
wheel=next(x for x in metadata['urls'] if x['filename']=='coverage-7.17.3-py3-none-any.whl');assert wheel['url'].startswith('https://files.pythonhosted.org/')
with urllib.request.urlopen(wheel['url'],timeout=30) as f:binary=f.read()
assert hashlib.sha256(binary).hexdigest()==wheel['digests']['sha256'];assert len(binary)==wheel['size']
out.mkdir();archive=out/wheel['filename'];archive.open('xb').write(binary);runtime=out/'runtime';runtime.mkdir()
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():
  p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and not name.endswith(('.so','.pyd','.dll'))
 z.extractall(runtime)
report=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tool='coverage.py',version='7.17.3',sourceMetadata=url,wheelUrl=wheel['url'],wheelFile=wheel['filename'],sha256=wheel['digests']['sha256'],size=wheel['size'],runtime=str(runtime),install='PURE_WHEEL_UNZIP_OUTSIDE_GIT_NO_GLOBAL_PIP',purpose='Pure Python management helper tool line/branch measurement only; no backend SDK/Java class activity',vendorProvenanceAttestationVerified=False)
(e/'coverage-toolchain.json').open('x').write(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ['actualExit','tool','version','sha256','size']})
