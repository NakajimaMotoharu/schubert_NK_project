"""Read-only qualification of one completed normal-artifact run; never starts product code."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,re,xml.etree.ElementTree as E,datetime,shutil
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';p=runs/'pg18700-correlated-log-n12-twentyfour-unit-v1'
out=root/'evidence/01_PT/020_NK-CHR-001/evidence/PG18700-correlated-log-n12-twentyfour-v1'
assert not out.exists();h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
m=json.loads((p/'manifest.safe.json').read_text());b=m['begin'];source='84925ff0685a755768f7c54507cbfd6ed9f7fc46'
assert m['source']==source and m['productionCoreMain']=='b09393b0e746b55fd480176d57996d65bd76a95d'
assert m['actualExit']==0 and m['tests']==24 and all(m[k]==0 for k in ['failures','errors','skipped'])
for n,x in m['stages'].items():
 assert x['actualExit']==0 and not x['timedOut'] and x['startUTC']<=x['endUTC']
 assert h(p/(n+'.stdout'))==x['stdoutSha256'] and h(p/(n+'.stderr'))==x['stderrSha256']
for f,v in b['characterizationMainInputs'].items():
 assert h(root/f)==v and hashlib.sha256(subprocess.check_output(['git','show',source+':'+f],cwd=root)).hexdigest()==v
for f,v in b['dependencies'].items():assert h(f)==v
for f,v in b['toolHashes'].items():assert h(f)==v
comp=runs/'pg18694-correlated-log-n12-final-compile-v1';assert h(comp/'manifest.safe.json')==b['compileManifestSha256']
for f,v in b['testClassHashes'].items():assert h(comp/'test-classes'/f)==v
classes=set(b['selectedClasses']);assert len(classes)==5
expected=set()
for cls in classes:
 f=root/'program/characterization/tests/java'/Path(cls.replace('.','/')+'.java')
 methods=re.findall(r'@Test\s+(?:public\s+)?void\s+(\w+)\s*\(',f.read_text())
 assert methods
 expected.update((cls,n) for n in methods)
assert len(expected)==24
actual=[];originalXml={}
for f in sorted((p/'xml').glob('TEST-*.xml')):
 originalXml[str(f)]=h(f)
 for c in E.parse(f).getroot().findall('.//testcase'):
  assert not c.findall('failure') and not c.findall('error') and not c.findall('skipped')
  name=c.get('name');assert name.endswith('()') and name.count('(')==1
  actual.append((c.get('classname'),name[:-2]))
assert len(actual)==24 and len(set(actual))==24 and set(actual)==expected
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==5 and '--select-method' not in cmd
assert {cmd[i+1] for i,v in enumerate(cmd[:-1]) if v=='--select-class'}==classes
assert '--fail-if-no-tests' in cmd and any('append=false' in x and 'sessionid='+b['session'] in x for x in cmd)
stdout=(p/'unit.stdout').read_text()
for s in ['24 tests found','24 tests started','24 tests successful','0 tests aborted','0 tests skipped','0 tests failed','0 containers aborted']:assert s in stdout
jar=next(Path(f) for f in b['dependencies'] if f.endswith('schubert-characterization-0.1.0-SNAPSHOT.jar'))
physical={}
with zipfile.ZipFile(jar) as z:
 for f in (p/'component').rglob('*.class'):
  n=str(f.relative_to(p/'component'));assert f.read_bytes()==z.read(n);physical[n[:-6]]=h(f)
assert len(physical)==9 and set(physical)==set(m['physical'])
info=(p/'classinfo.stdout').read_text();execinfo=(p/'execinfo.stdout').read_text();assert execinfo.count('Session "')==1 and 'Session "'+b['session']+'"' in execinfo
classids={n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',info)}
execids={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',execinfo,re.M)}
assert set(classids)==set(physical)
for n,(crc,_,_) in execids.items():
 if n in physical:assert classids[n]==crc
report=E.parse(p/'coverage.xml').getroot();coverage={};qualified=[]
for c in report.findall('.//package/class'):
 n=c.get('name');assert n in physical
 counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))} for x in c.findall('counter')}
 coverage[n]=counters
 if all(v['missed']==0 for k,v in counters.items() if k in ['LINE','METHOD','CLASS','BRANCH']):
  qualified.append(n);assert n in execids and classids[n]==execids[n][0]
assert set(qualified)=={n for n in physical if n.split('/')[-1].split('$')[0] in ['ArtifactComparator','TargetAdapter','CorrelatedLogEvidenceValidator']}
assert len(qualified)==5
out.mkdir(parents=True)
for name in ['unit.stdout','unit.stderr','coverage.xml','coverage.csv','classinfo.stdout','execinfo.stdout','jacoco.exec','begin.safe.json','manifest.safe.json']:
 shutil.copyfile(p/name,out/name)
for name in m['stages']:
 for suffix in ['begin.safe.json','process.safe.json','exit.safe.json']:
  shutil.copyfile(p/(name+'-'+suffix),out/(name+'-'+suffix))
# Original XML stays immutable locally; publish testcase results without machine/system properties.
suite=E.Element('testsuite',tests='24',failures='0',errors='0',skipped='0')
for cls,n in sorted(actual):E.SubElement(suite,'testcase',classname=cls,name=n+'()')
E.ElementTree(suite).write(out/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
value={'actualExit':0,'atJST':datetime.datetime.now().astimezone().isoformat(),'source':source,'productionCoreMain':m['productionCoreMain'],'originalManifest':{'path':str(p/'manifest.safe.json'),'sha256':h(p/'manifest.safe.json')},'originalXml':originalXml,'tests':24,'testClasses':5,'failures':0,'errors':0,'skipped':0,'aborted':0,'sourceAndSelectorBindingsChecked':True,'normalJarSha256':h(jar),'testSourceMethods':sorted([list(x) for x in expected]),'sameSource':True,'session':b['session'],'physicalHashes':physical,'physicalClassIds':classids,'execMatches':{n:execids[n] for n in physical if n in execids},'coverage':coverage,'fourCountersWholeSourceQualified':['ArtifactComparator.java','CorrelatedLogEvidenceValidator.java','TargetAdapter.java'],'partiallyCoveredNotQualified':['GateCli.java','GateContractValidator.java'],'noOldExecUnion':True,'exclusions':[],'probeHitsAreNotFourSourceCounters':True,'compilerFilterPolicy':'UNCHANGED_JACOCO_0_8_15_DEFAULT_NO_MANUAL_EXCLUSION','nativeOrRealChr':False,'actualCapture':False,'newAccepted':0,'formalUpdated':False,'files':{str(f.relative_to(out)):h(f) for f in out.iterdir() if f.is_file()}}
(out/'manifest.json').write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'actualExit':0,'tests':24,'wholeSourcesQualified':3,'physicalFull':len(qualified),'partialSources':2,'manifestSha256':h(out/'manifest.json')}))
