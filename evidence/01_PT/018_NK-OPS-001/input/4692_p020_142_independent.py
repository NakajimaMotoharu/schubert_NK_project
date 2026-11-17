"""Whole142 from a single genuine successful changed-source run, all physical/Code retained."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';p=w/'pg37322-p020-remote142-recovered';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
u=ld(p/'terminal.json');begin=ld(p/'begin.json');cfg=ld(w/'pg37318-p020-public-package-v1/package.json');audit=ld(b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json');static=ld(b/'evidence/PG37316-p020-fixture-fix-static-v1/manifest.json')
assert u['actualExit']==0 and u['source']==cfg['source']==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert all(x['actualExit']==0 and not x['timedOut'] for x in u['stages'].values());assert u['sourceInputsUnchanged'] and u['baselineUnchanged'] and begin['sourceHashes']==cfg['sourceHashes'];assert all(sha(r/n)==h for n,h in cfg['sourceHashes'].items());assert all(sha(p/n)==h for n,h in u['files'].items());assert all(sha(p/'mainclasses'/n)==h for n,h in u['mainClasses'].items());assert u['mainClasses']==static['mainClassHashes'] and len(u['mainClasses'])==16
assert all(sha(p/'testclasses'/n)==h for n,h in u['testClasses'].items());assert not any('CurrentCharacterizationTest' in n or 'Native' in n for n in u['testClasses'])
expected=set()
for suite in audit['selectedWholeSuites']:
 for method in suite['ordinaryMethods']:
  declarations=re.findall(r'void\s+'+re.escape(method)+r'\(([^)]*)\)',(r/suite['path']).read_text())
  assert len(declarations)==1;parameter=declarations[0].strip();assert not parameter or re.fullmatch(r'@TempDir\s+Path\s+\w+',parameter);expected.add(('dev.codex.schubert.characterization.'+suite['suite'],method+('()' if not parameter else '(Path)')))
 if suite['parameterizedInvocations']:
  for i in range(1,8):expected.add(('dev.codex.schubert.characterization.'+suite['suite'],'rejectsEveryNonPassExecutionStatus(String)['+str(i)+']'))
for name in ['CommonValueContractTest','CharacterizationIoScopeTest','GateOutputFailureContractTest']:
 text=(r/'program/characterization/tests/java/dev/codex/schubert/characterization'/(name+'.java')).read_text();methods=re.findall(r'@Test\s+void\s+(\w+)\(\)',text);assert len(methods)=={'CommonValueContractTest':5,'CharacterizationIoScopeTest':7,'GateOutputFailureContractTest':6}[name]
 expected.update(('dev.codex.schubert.characterization.'+name,method+'()') for method in methods)
def valid(c):return not any(c.findall('.//'+tag) for tag in ['failure','error','skipped']) and all(child.tag in ['system-out','system-err'] for child in c)
assert valid(E.fromstring('<testcase><system-out>metadata</system-out></testcase>'))
for tag in ['failure','error','skipped','unknown']:assert not valid(E.fromstring('<testcase><'+tag+'/></testcase>'))
cases=[]
for name,h in u['xmlHashes'].items():
 assert sha(p/'xml'/name)==h;tree=E.parse(p/'xml'/name).getroot();assert all(int(tree.get(k,0))==0 for k in ['failures','errors','skipped'])
 for c in tree.findall('testcase'):assert valid(c);cases.append((c.get('classname'),c.get('name')))
assert len(cases)==len(set(cases))==len(expected)==142 and set(cases)==expected
ex=(p/'execinfo.log').read_text();assert ex.count('Session "')==1 and 'Session "PG37322-COMMON142"' in ex
initializing=set(re.findall(r"Initializing '([^']+)'",(p/'class-init.log').read_text()));assert not any(n.startswith(('dev/codex/schubert/nk/','com/microsoft/playwright/')) for n in initializing);assert 'dev/codex/schubert/characterization/CurrentCharacterizationTest' not in initializing
probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
def crc64(raw):
 assert int.from_bytes(raw[6:8],'big')==69;value=0
 for byte in raw:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
ids={n[:-6]:crc64((p/'mainclasses'/n).read_bytes()) for n in u['mainClasses']};qualified=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests']==12
for pin in qualified['dependencies']+[dict(path=str(r/qualified['source']['path']),sha256=qualified['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
out=b/'evidence/PG37324-p020-whole142-independent-v1';assert not out.exists();out.mkdir();cmd=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[x['path'] for x in qualified['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(p/'jacoco.exec'),*[str(p/'mainclasses'/n) for n in sorted(u['mainClasses'])]]
with (out/'unfiltered.stdout').open('xb') as stdout,(out/'unfiltered.stderr').open('xb') as stderr:child=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=120)
assert child.returncode==0;classes={};methods=[]
for line in (out/'unfiltered.stdout').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':row=dict(name=f[1],id=f[2],dataPresent=f[3]=='true',probes=int(f[4]),access=int(f[5]),counters={});classes[f[1]]=row;offset=6
 else:assert f[0]=='METHOD';row=dict(className=f[1],name=f[2],descriptor=f[3],access=int(f[4]),counters={});methods.append(row);offset=5
 for item in f[offset:]:key,miss,hit=item.split(':');row['counters'][key]=dict(missed=int(miss),covered=int(hit))
assert set(classes)==set(ids) and all(x['id']==ids[n] for n,x in classes.items());code={n for n,c in classes.items() if sum(c['counters']['METHOD'].values())>0};no_code=set(ids)-code;assert len(code)==12 and len(no_code)==4
assert all(n in probes and probes[n]['crc']==ids[n] and probes[n]['hit']>0 for n in code);assert all(sum(classes[n]['counters'][k].values())==0 for n in no_code for k in ['METHOD','LINE','CLASS','BRANCH','INSTRUCTION']);assert all(n not in probes for n in no_code)
totals={k:{role:sum(c['counters'][k][role] for c in classes.values()) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']};standard={x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in E.parse(p/'coverage.xml').getroot().findall('counter')}
for name in ['terminal.json','begin.json','jacoco.exec','coverage.xml','execinfo.log','maincompile.log','testcompile.log','unit.log']:shutil.copyfile(p/name,out/name)
shutil.copytree(p/'xml',out/'xml')
with (out/'class-init.log.gz').open('xb') as f:f.write(gzip.compress((p/'class-init.log').read_bytes(),mtime=0))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=u['source'],toolSource=u['sourceCore'],productionCoreMainUnchanged=cfg['productionCoreMainUnchanged'],run='PG37322-COMMON142',expected=142,success=142,failed=0,errors=0,skipped=0,notRun=0,wholeSuites=20,mainSources=6,mainPhysical=16,codePhysical12=True,noCodeInterfacesRetained=sorted(no_code),cases=[dict(className=c,name=n,result='PASS') for c,n in sorted(cases)],standardCounters=standard,rawCounters=totals,rawMissedMethods=[m for m in methods if any(x['missed'] for x in m['counters'].values())],allMethods=methods,classIds=ids,classSha256=u['mainClasses'],testHelperSha256=u['testClasses'],classMeasurements=classes,sourceTestPins=cfg['sourceHashes'],sdkPins=cfg['sdkHashes'],sourceBaselineUnchanged=True,xmlNegativeChecks=4,realProductNativeBrowserDbRootInitializations=0,oldExecUnion=False,manualCoverageExclusions=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,actualBytesStaticProof=ref(b/'evidence/PG37316-p020-fixture-fix-static-v1/manifest.json'),sourceStaticProof=ref(b/'evidence/PG37304-p020-static-admission-v1/manifest.json'),files={str(x.relative_to(out)):sha(x) for x in sorted(out.rglob('*')) if x.is_file()},unfilteredCommand=cmd,unfilteredExit=child.returncode)
(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,success=142,standard=standard,raw=totals,rawMissingMethods=len(v['rawMissedMethods']),newAcceptance=0)))
