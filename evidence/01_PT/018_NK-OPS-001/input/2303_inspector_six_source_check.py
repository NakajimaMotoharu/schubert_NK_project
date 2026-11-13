"""Independent minimal-delta normalization and Root source-only checks. No product execution."""
from pathlib import Path
import subprocess,json,hashlib,datetime as dt,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';a=b/'evidence/PG29400-inspector-six-main-source-repair-v1';o=b/'evidence/PG29402-inspector-six-main-source-check-v1';assert not o.exists();o.mkdir();tc=r.parent/'toolchain';fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-'];patches=json.loads((a/'patches.json').read_text());proof=[]
for v in patches:
 p=r/v['path'];old=(a/(p.stem+'.before.java.txt')).read_text();assert hashlib.sha256(old.encode()).hexdigest()==v['beforeSha256'];expected=old
 for before,after in v['pairs']:assert expected.count(before)==1;expected=expected.replace(before,after)
 normalized=subprocess.check_output(fmt,input=expected.encode());assert normalized==p.read_bytes()
 inverse=expected
 for before,after in reversed(v['pairs']):assert inverse.count(after)==1;inverse=inverse.replace(after,before)
 assert inverse==old;proof.append(dict(path=v['path'],normalizedForwardEqualsActual=True,inverseEqualsWholeOriginal=True,declaredReplacements=len(v['pairs']),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
sources=o/'sources.txt';sources.write_text(''.join(str(r/v['path'])+'\n' for v in patches));base=b/'evidence/PG29376-env10-static-v1';prior=json.loads((base/'manifest.json').read_text());stages={}
for name in ['pmd','checkstyle']:
 cmd=prior['stages'][name]['command'];cmd=[x.replace(str(base),str(o)) for x in cmd];start=dt.datetime.now(dt.timezone.utc).isoformat();p=subprocess.run(cmd,cwd=r,capture_output=True,timeout=120);(o/(name+'.stdout')).write_bytes(p.stdout);(o/(name+'.stderr')).write_bytes(p.stderr);stages[name]=dict(actualExit=p.returncode,command=cmd,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat());assert p.returncode in ([0,4] if name=='pmd' else [0])
raw=[]
for f in ET.parse(o/'pmd.xml').getroot():
 if f.tag.endswith('file'):
  for v in f:raw.append(dict(path=f.attrib['name'],rule=v.attrib.get('rule'),line=v.attrib.get('beginline'),message=(v.text or '').strip()))
assert not list(ET.parse(o/'checkstyle.xml').getroot().iter('error'));m=dict(actualExit=0,checkKind='SOURCE_ONLY_NOT_COMPILER_OR_PT',originalMainSources=6,proof=proof,rootCheckstyleFindings=0,rootPmdRaw=raw,stages=stages,productTestsExecuted=0,compiled=False,coverage=None,runtimeQualified=False);(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeOriginalInverse=6,rootCheckstyle=0,pmdRaw=raw),ensure_ascii=False))
