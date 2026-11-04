from pathlib import Path
import ast,copy,hashlib,json,re,shutil,xml.etree.ElementTree as E
from source_evidence_binding import bind
R=Path('/home/mini/codex/project1/work/pgpt-foundation');S=Path(__file__).parent;D=R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104';O=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18590-config-loaders-current-whole10-v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for p in [Path(__file__),S/'driver.py']:
 text=p.read_text();compile(text,str(p),'exec')
 for n in ast.walk(ast.parse(text)):
  if isinstance(n,ast.Call):
   names=[k.arg for k in n.keywords if k.arg is not None];assert len(names)==len(set(names))
raw=json.loads((S/'manifest.safe.json').read_text());assert H(S/'manifest.safe.json')=='38133b73326a7e380e48b049dc082d4269316ec19c3b1e56c7d83dc0acdd0b99';assert raw['actualExit']==0 and raw['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c';assert all(H(S/n)==h for n,h in raw['files'].items());assert all(H(p)==h for p,h in raw['toolAndDependencyHashes'].items());assert all(H(R/p)==h for p,h in raw['begin']['normalMainInputHashes'].items());assert all(H(R/p)==h for p,h in raw['begin']['testInputHashes'].items())
plan=json.loads(next(D.glob('656_*.json')).read_text());physical={r['main'].split('/main/java/')[1].removesuffix('.java') for r in plan['rows']};expected={(f'dev.codex.schubert.nk.{r["module"]}.bootstrap.'+('Api' if r['module']=='api' else 'Web')+'ConfigurationLoaderTest',m) for r in plan['rows'] for m in r['testIds']};cases=[];env={};roots=[]
for p in (S/'xml').glob('TEST-*.xml'):
 e=E.parse(p).getroot();roots.append((p,e));assert int(e.get('tests'))==len(e.findall('testcase')) and all(int(e.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for c in e.findall('testcase'):
  assert not any(t.tag in ['failure','error','skipped'] for t in c);assert c.get('name').endswith('()');cases.append((c.get('classname'),c.get('name')[:-2]))
 for v in e.findall('properties/property'):
  if v.get('name') in ['os.name','os.arch','os.version','java.version','java.runtime.version','java.vendor']:env[v.get('name')]=v.get('value')
assert len(cases)==len(set(cases))==10 and set(cases)==expected
cov=E.parse(S/'coverage.xml').getroot();assert {c.get('name') for c in cov.findall('.//class')}==physical
counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in cov.findall('counter')};assert all(counters[k]=={'missed':0,'covered':v} for k,v in [('LINE',38),('METHOD',10),('CLASS',2),('BRANCH',20)])
sessions=cov.findall('sessioninfo');assert len(sessions)==1 and sessions[0].get('id')==raw['begin']['session'];execs=re.findall(r'^([0-9a-f]{16})\s+\d+ of\s+\d+\s+(dev/[^\s]+)$',(S/'execinfo.stdout').read_text(),re.M);analyzed=re.findall(r'class 0x([0-9a-f]{16})\s+(dev/[^\s]+)',(S/'classinfo.stdout').read_text());assert len(execs)==len(analyzed)==2 and set(execs)==set(analyzed) and {n for _,n in execs}==physical
pmd=E.parse(S/'pmd.xml').getroot();findings=[dict(file=f.get('name').removeprefix(str(R)+'/'),rule=v.get('rule'),line=int(v.get('beginline')),message=' '.join(''.join(v.itertext()).split())) for f in pmd for v in f if v.tag.rsplit('}',1)[-1]=='violation'];assert len(findings)==4 and {f['rule'] for f in findings}=={'DoNotUseThreads'};assert not any(v.tag.rsplit('}',1)[-1] in ['error','configerror'] for v in pmd.iter());assert not E.parse(S/'checkstyle.xml').getroot().findall('.//error')
initialized=sorted({m.group(1).replace('/','.') for line in (S/'class-init.log').read_text().splitlines() if (m:=re.search(r"Initializing '[^']*?(dev/codex/schubert/[^']+)'",line)) and '$$Lambda' not in m.group(1) and 'ConfigurationLoaderTest' not in m.group(1)})
allowed={'dev.codex.schubert.nk.'+s for s in ['api.bootstrap.ApiConfigurationLoader','web.bootstrap.WebConfigurationLoader','api.bootstrap.ApiNonSecretConfig','web.bootstrap.WebNonSecretConfig','bootstrap.ChildStartupContext','storage.ServiceConfigFiles','storage.ServiceConfigFiles$Contents','storage.ServiceConfigFiles$Service','storage.ServiceConfigFiles$NioIo','storage.StorageIdentity','storage.DirectoryCalls','storage.LinuxDirectoryCalls','storage.StorageIoException','storage.StorageIoException$Reason']};assert set(initialized)<=allowed;assert not (set(initialized)|{'UNKNOWN_NOT_REVIEWED'})<=allowed
baseline=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18472-current3008-resource-owner-domains-v1/manifest.json';b=json.loads(baseline.read_text());old={(x['classname'],x['name'].removesuffix('()')) for x in b['cases']};overlap=sorted(set(cases)&old)
result=dict(actualExit=0,source=raw['source'],testSource=plan['source'],proofKind='CURRENT_MAIN_TWO_WHOLE_LOADER_UNITS_WITH_FOUR_RAW_STATIC_FINDINGS',tests=10,testClasses=2,junitXmlSuites=len(roots),cases=[dict(classname=c,name=m,result='PASS') for c,m in sorted(cases)],failures=0,errors=0,skipped=0,aborted=0,counters=counters,session=sessions[0].get('id'),physical=raw['begin']['physical'],executedAndAnalyzedCRC=[dict(crc=c,name=n) for c,n in execs],crcMismatch=0,oldExecCombined=False,physicalClosureComplete=True,manualExclusions=[],rawManifestSha256=H(S/'manifest.safe.json'),actualStages=raw['stages'],environment=env,effects=plan['effects'],initializedProductClasses=initialized,unexpectedProductInitialized=[],static=dict(pmdFindings=4,processingErrors=0,checkstyle=0,rawFindings=findings,applicability='4 own finite host-unit executor lifecycle findings: both pools collect all32 Futures then try-with-resources close; not deployed JavaEE thread creation. Raw findings/exit4 retained; no suppression; whole F03 not accepted.'),baselineRegistrySha256=H(baseline),existingCasesOverlapping=overlap,registryUpdated=False,eligibleUnmergedQualification=dict(methods=10,testClasses=2,wholeSources=2,physicalClasses=2),canonicalOwners={r['main']:r['owner'] for r in plan['rows']},formalUpdated=False,newWbsAccepted=0,whole451Accepted=False,effortPercent=None,firstVChanged=False,root18474OriginalTerminal='UNRECOVERED',postProductTestsReexecuted=0)
def assess(x):
 assert x['source']==raw['source'] and x['testSource']==plan['source'];assert x['tests']==10 and x['failures']==x['errors']==x['skipped']==x['aborted']==0
 assert len(x['cases'])==len({(c['classname'],c['name']) for c in x['cases']})==10 and {(c['classname'],c['name']) for c in x['cases']}==expected
 assert x['session']==sessions[0].get('id') and x['crcMismatch']==0 and not x['oldExecCombined'] and not x['formalUpdated'];assert set(x['physical'])==physical;assert all(x['counters'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
assess(result);neg=[]
for label,change in [('source',lambda x:x.update(source='0'*40)),('testsource',lambda x:x.update(testSource='0'*40)),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),('skip',lambda x:x.update(skipped=1)),('session',lambda x:x.update(session='other')),('crc',lambda x:x.update(crcMismatch=1)),('union',lambda x:x.update(oldExecCombined=True)),('branch',lambda x:x['counters']['BRANCH'].update(missed=1)),('formal',lambda x:x.update(formalUpdated=True))]:
 bad=copy.deepcopy(result);change(bad)
 try:assess(bad)
 except AssertionError:neg.append(label)
 else:raise AssertionError(label)
assert not O.exists();O.mkdir();(O/'xml').mkdir()
for p,e in roots:
 clean=E.Element('testsuite',{k:v for k,v in e.attrib.items() if k in ['name','tests','failures','errors','skipped','time','timestamp']})
 for c in e.findall('testcase'):E.SubElement(clean,'testcase',{k:v for k,v in c.attrib.items() if k in ['classname','name','time']})
 E.ElementTree(clean).write(O/'xml'/p.name,encoding='utf-8',xml_declaration=True)
for n in ['coverage.xml','coverage.csv','driver.py','post.py']:shutil.copyfile(S/n,O/n)
result.update(metadataNegativeLabels=neg,postBodySha256=H(__file__),literalKeywordDuplicateAstChecked=['driver.py','post.py'],files={str(p.relative_to(O)):H(p) for p in O.rglob('*') if p.is_file()});put(O/'manifest.json',result)
post=dict(actualExit=0,source=raw['source'],publicManifest=str((O/'manifest.json').relative_to(R)),publicManifestSha256=H(O/'manifest.json'),sourceEvidenceRefs=bind([(O/'manifest.json',H(O/'manifest.json'))],raw['source']),tests=10,testClasses=2,junitXmlSuites=len(roots),counters=counters,crcMismatch=0,negativeLabels=neg,baselineOverlap=overlap,registryUpdated=False,productTestsReexecuted=0,originalFailure='658/49faa7/1 beforebody',repairBug='BUG2257',horizontal='YKT2002')
put(D/'657_APIWeb設定loader実十件・四counterと独立post.json',post)
print(json.dumps(dict(actualExit=0,tests=10,testClasses=2,junitXmlSuites=len(roots),counters=counters,pmd=4,checkstyle=0,negativeChecks=len(neg),baselineOverlap=len(overlap),manifestSha256=H(O/'manifest.json'),postSha256=H(D/'657_APIWeb設定loader実十件・四counterと独立post.json')),ensure_ascii=False))
