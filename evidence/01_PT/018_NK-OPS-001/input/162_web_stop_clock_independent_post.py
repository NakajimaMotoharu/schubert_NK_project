"""Independently bind existing raw results only; no Product/Test or analyzer subprocess."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
unit=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22024-web-stop-clock-six-unit-v2';m=load(unit/'manifest.json');assert sha(unit/'manifest.json')=='4c00f5957b5549994a2a270332c4fd85e48e51d8d95d37467037f1c9ac6ef3e3'
assert m['actualExit']==0 and m['tests']==6 and all(m[k]==0 for k in ['failures','errors','skipped']) and m['newUniqueMethods']==1 and m['requalifiedExistingMethods']==5
assert m['source']=='4c719e2aeb1dffaa6e7d0de6c451574cd896f192' and m['productionCoreMain']=='54d5c19da0117db49edff7b5ae46207fdee59acc'
for n,h in m['files'].items():assert sha(unit/n)==h
for n,h in m['begin']['inputHashes'].items():assert sha(r/n)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()
raw=Path(m['originalManifest']['path']);assert sha(raw)==m['originalManifest']['sha256'];rawm=load(raw);assert rawm['cases']==m['cases'] and rawm['stages']==m['stages']
for key,s in m['stages'].items():assert s['actualExit']==0 and not s['timedOut'] and sha(raw.parent/(key+'.stdout'))==s['stdoutSha256'] and sha(raw.parent/(key+'.stderr'))==s['stderrSha256']
cases=[];environment=[]
for p in sorted((raw.parent/'xml').glob('TEST-*.xml')):
 root=E.parse(p).getroot();assert all(int(root.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for t in root.findall('testcase'):
  assert not any(t.findall(k) for k in ['failure','error','skipped']);cases.append((t.get('classname'),t.get('name')))
 props={v.get('name'):v.get('value') for v in root.findall('properties/property')};environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStopTest.java';methods=re.findall(r'@Test\s+void\s+(\w+)\(',Path(test).read_text());assert len(cases)==len(set(cases))==len(methods)==6 and {v+'()' for v in methods}=={v for _,v in cases}
normalp=w/'pg22012-web-stop-clock-six-main-compile-v1/manifest.safe.json';normal=load(normalp);assert sha(normalp)=='e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640' and normal['source']==m['productionCoreMain'] and normal['actualExit']==0
assert len(normal['begin']['inputHashes'])==1036 and len(normal['normalPhysicalClassHashes'])==1845
for n,h in normal['begin']['inputHashes'].items():assert sha(r/n)==h
for v in normal['jars'].values():assert sha(v['path'])==v['sha256']
with zipfile.ZipFile(normal['jars']['web']['path']) as z:
 for n,h in m['physical'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
coverage={n.get('name'):{c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in n.findall('counter')} for n in E.parse(unit/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage'] and set(coverage)==set(m['physical']) and len(coverage)==2
pkg='dev/codex/schubert/nk/web/bootstrap/';assert coverage[pkg+'WebRuntimeStop$Step']=={} and m['fourCounters']=={k:dict(covered=v,missed=0) for k,v in [('LINE',16),('METHOD',3),('CLASS',1),('BRANCH',4)]}
ids={n:crc for crc,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(unit/'classinfo.stdout').read_text())};assert set(ids)==set(coverage);ex=(unit/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22024-web-stop-clock-six-unit-v2-WEBSTOP"' in ex
n=pkg+'WebRuntimeStop';assert re.search(r'^'+ids[n]+r'\s+12 of\s+12\s+'+re.escape(n)+r'$',ex,re.M)
initialised=set(re.findall(r"Initializing '([^']+)",(unit/'original-class-init.stdout').read_text()));held=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'];assert not set(held)&initialised and m['heldFourInitialisations']==0
staticp=w/'pg22014-web-stop-clock-six-static-reactor-v1/manifest.safe.json';sb=load(staticp);assert sha(staticp)=='b2e2d9695ba4734698d2378d51be117cbdfd9368fbbabc6cd8b42ead5d387360' and sb['actualExit']==0 and len(sb['reports'])==6 and sb['normalCompileManifestSha256']==sha(normalp)
for v in sb['reports'].values():assert sha(v['path'])==v['sha256'] and v['bugs']==v['missing']==v['errors']==0
stylep=w/'pg22022-web-stop-clock-style-v2/raw-manifest.safe.json';style=load(stylep);assert len(style['findings'])==1 and style['findings'][0]['attributes']['rule']=='AvoidCatchingGenericException' and style['stages']['pmd']['actualExit']==4 and style['stages']['checkstyle']['actualExit']==0 and not style['processingErrors']
for n,h in style['inputHashes'].items():assert sha(n)==h
old=load(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG20154-current-d8-context-requalification-v1/review.json')
def find(v):
 if isinstance(v,dict):
  if v.get('rawFinding',{}).get('path')==style['findings'][0]['path']:yield v
  else:
   for x in v.values():yield from find(x)
 elif isinstance(v,list):
  for x in v:yield from find(x)
prior=list(find(old));assert len(prior)==1 and prior[0]['actualViolation'] is False
current=style['findings'][0];attributes=dict(current['attributes']);oldattributes=dict(prior[0]['rawFinding']['attributes']);attributes.pop('beginline');attributes.pop('endline');oldattributes.pop('beginline');oldattributes.pop('endline');assert attributes==oldattributes and current['message']==prior[0]['rawFinding']['message']
line=Path(current['path']).read_text().splitlines()[int(current['attributes']['beginline'])-1];assert 'RuntimeException failure' in line and 'SessionStoreException.preserveFatal(failure);' in Path(current['path']).read_text()
red=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22008-web-stop-wrap-original-red-v1/manifest.json';redm=load(red);assert redm['actualExit']==1 and redm['errors']==1 and redm['newAcceptedTests']==0 and redm['productionCoreMain']=='56720d75714f60d7e31da59c3da8c02baf05de52'
for n,h in redm['files'].items():assert sha(red.parent/n)==h
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22026-web-stop-clock-independent-post-v1';assert not out.exists();out.mkdir();files={}
for name,p in [('normal.json',normalp),('six-static.json',staticp),('style-raw.json',stylep),('pmd.xml',stylep.parent/'pmd.xml'),('checkstyle.xml',stylep.parent/'checkstyle.xml'),('clock-comparison-search.json',w/'pg22004-clock-comparison-search.json')]:shutil.copyfile(p,out/name);files[name]=sha(out/name)
for role,v in sb['reports'].items():name='spotbugs-'+role+'.xml';shutil.copyfile(v['path'],out/name);files[name]=sha(out/name)
for key in ['pmd','checkstyle']:
 for suffix in ['stdout','stderr','exit.safe.json','begin.safe.json']:
  name=key+'-'+suffix if suffix.endswith('.json') else key+'.'+suffix;p=stylep.parent/name;shutil.copyfile(p,out/name);files[name]=sha(out/name)
judgment=dict(raw=current,classification='CONTEXTUAL_NONAPPLICABLE',actualViolation=False,prior=prior[0],reason='Exact unchanged catch/normalization role: preserve fatal identity then fixed IOException, do not catch NPE as success; only deadline signed comparison changed. Existing independent 004/005 confirm fixed failure/unchanged phase/Error identity. No rule suppression or runtime/native acceptance.')
write(out/'style-applicability.json',judgment);files['style-applicability.json']=sha(out/'style-applicability.json')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],unitManifest=dict(path=str((unit/'manifest.json').relative_to(r)),sha256=sha(unit/'manifest.json')),redManifest=dict(path=str(red.relative_to(r)),sha256=sha(red)),tests=6,newUniqueTests=1,requalifiedExistingTests=5,newWholeSourceProofs=0,originalSourceStatus='Already FOUR100 in fixed seed; changed-source requalification only',coverage=coverage,fourCounters=m['fourCounters'],physical=2,noCodeInterfaces=1,classIds=ids,expectedSession='PG22024-web-stop-clock-six-unit-v2-WEBSTOP',heldFourInitialisations=0,environment=environment,staticSixZero=True,pmdRaw=1,pmdRawExit=4,pmdApplicable=0,checkstyle=0,oldExecUnion=False,manualCoverageExclusions=[],files=files,newAcceptance=0,whole451Accepted=False,formalUpdated=False,effortRate=None,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
write(out/'manifest.json',value);print(json.dumps(dict(actualExit=0,tests=6,newUnique=1,fourCounters=m['fourCounters'],manifestSha256=sha(out/'manifest.json'))))
