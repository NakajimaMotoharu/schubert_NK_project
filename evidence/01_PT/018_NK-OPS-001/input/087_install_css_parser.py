"""Install two pinned public pure-Python CSS parser wheels into a new owned tool directory only."""
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse,zipfile,io,datetime,sys
BASE=Path('/home/mini/codex/project1/work/toolchain/css-contract-parser-1.4.0');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if BASE.exists():
 m=json.loads((BASE/'manifest.json').read_text());assert all(sha(BASE/p)==h for p,h in m['installedFiles'].items());print(json.dumps(dict(existingVerified=True,newInstall=False,manifestSha256=sha(BASE/'manifest.json'))));sys.exit(0)
BASE.mkdir();(BASE/'site').mkdir();(BASE/'wheels').mkdir();rows=[]
for name,version,allowed in [('tinycss2','1.4.0',{'tinycss2','tinycss2-1.4.0.dist-info'}),('webencodings','0.5.1',{'webencodings','webencodings-0.5.1.dist-info'})]:
 url=f'https://pypi.org/pypi/{name}/{version}/json'
 with urllib.request.urlopen(url,timeout=30) as response:meta=response.read()
 d=json.loads(meta);assert d['info']['version']==version;items=[x for x in d['urls'] if x['filename'].endswith('.whl') and x['packagetype']=='bdist_wheel'];assert len(items)==1;item=items[0];assert urllib.parse.urlsplit(item['url']).hostname=='files.pythonhosted.org' and item['url'].startswith('https://')
 with urllib.request.urlopen(item['url'],timeout=30) as response:blob=response.read()
 h=hashlib.sha256(blob).hexdigest();assert h==item['digests']['sha256'];p=BASE/'wheels'/item['filename'];p.write_bytes(blob)
 with zipfile.ZipFile(io.BytesIO(blob)) as archive:
  for entry in archive.infolist():
   parts=Path(entry.filename).parts;assert parts and parts[0] in allowed and not entry.filename.startswith('/') and '..' not in parts and not (entry.external_attr>>16)&0o170000==0o120000
   if not entry.is_dir():dest=BASE/'site'/entry.filename;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.read(entry))
 rows.append(dict(name=name,version=version,metadataUrl=url,metadataSha256=hashlib.sha256(meta).hexdigest(),wheelUrl=item['url'],wheelFilename=item['filename'],wheelSha256=h,wheelBytes=len(blob)))
files={str(p.relative_to(BASE)):sha(p) for p in (BASE/'site').rglob('*') if p.is_file()};m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,packages=rows,installedFiles=files,installation='hash-verified pure wheel extraction only, no setup/build script or global environment changes',producerSha256=sha(Path(__file__)),network='only public PyPI metadata and files.pythonhosted.org for these two wheels; no credentials/config/profiles read',reproduce='verify recorded exact wheel SHA then extract safe relative members into a fresh owned site; set PYTHONPATH to that site');(BASE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(installed=True,packages=[(x['name'],x['version']) for x in rows],manifestSha256=sha(BASE/'manifest.json'))))
