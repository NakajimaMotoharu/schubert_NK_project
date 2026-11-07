"""Whole original nine JDBC cases at changed Test source; independent Code/CRC/owned graph checks."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22664-schema-nine-unit-v1';META=RUNS/'pg22668-schema-nine-passive-metadata-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22670-schema-nine-independent-v1';SOURCE='d8935a18a98f1f3fb51fd1c6e54b7d5ac40d683a';CORE='7aed8eace7c844c2f79f2e39db766faf914890d5';BASE='dev/codex/schubert/nk/api/bootstrap/';TARGETS={BASE+'SchemaHistoryAdmission',BASE+'SchemaHistoryAdmission$Row',BASE+'JdbcAdmissionFailures'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 c=0
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^0xd800000000000000 if c&1 else c>>1
 return f'{c:016x}'
def main():
 assert not OUT.exists();m=load(U/'manifest.json');b=load(U/'begin.json');assert m['begin']==b and (b['source'],b['normalSource'])==(SOURCE,CORE);assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,9,0,0,0);assert b['expectedTests']==b['requalifiedExistingMethods']==9 and b['newMethods']==0
 for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+p],cwd=R)).hexdigest()
 for p,h in b['dependencies'].items():assert sha(p)==h
 for label,s in m['stages'].items():
  assert s['actualExit']==0 and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==s[stream+'Sha256']
 assert load(U/'unit-exit.safe.json')==m['stages']['unit'];cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and cmd[-1]=='dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest' and '--select-method' not in cmd and '--scan-classpath' not in cmd
 original=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22654-schema-wait-original-v1';op=load(original/'manifest.json');test=R/op['sourcePath'];assert sha(original/'SchemaHistoryAdmissionTest.java')==op['sourceSha256'];expected={('dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest',n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (original/'SchemaHistoryAdmissionTest.java').read_text())};assert len(expected)==9;cases=[];environment={}
 for p in sorted((U/'xml').glob('TEST-*.xml')):
  t=E.parse(p).getroot();assert not any(t.findall('.//'+x) for x in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in t.findall('testcase'))
  for x in t.findall('./properties/property'):
   if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:environment[x.get('name')]=x.get('value')
 assert len(cases)==len(set(cases))==9 and set(cases)==expected
 for x in ['9 tests found','9 tests started','9 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert x in (U/'unit.stdout').read_text()
 normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['source']==CORE and normal['actualExit']==0;physical={};ids={}
 with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
  family={n[:-6] for n in jar.namelist() if n.endswith('.class') and (n.startswith(BASE+'SchemaHistoryAdmission$') or n in [BASE+'SchemaHistoryAdmission.class',BASE+'JdbcAdmissionFailures.class'])};assert family==TARGETS
  for name in TARGETS:
   data=jar.read(name+'.class');physical[name]=hashlib.sha256(data).hexdigest();ids[name]=crc64(data);assert sha(U/'component'/(name+'.class'))==physical[name]
 assert m['physical']==physical;actualids={n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert actualids==ids;ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22664-SCHEMA-NINE"' in ex;probes={name:[c,int(hit),int(total)] for c,hit,total,name in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
 for n,c in ids.items():assert probes[n][0]==c and 0<probes[n][1]<=probes[n][2]
 tree=E.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in tree.findall('.//class')}==TARGETS;counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')};assert all(x['missed']==0 for x in counters.values());assert {k:counters[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=89,METHOD=8,CLASS=3,BRANCH=78);familyCoverage={cl.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in cl.findall('counter')} for cl in tree.findall('.//class')};assert all(all(c['missed']==0 for c in cs.values()) for cs in familyCoverage.values())
 counted={cl.get('name'):{x.get('name') for x in cl.findall('method')} for cl in tree.findall('.//class')};assert counted[BASE+'SchemaHistoryAdmission']=={'<init>','verify','inspect','require','required','unavailable'} and counted[BASE+'SchemaHistoryAdmission$Row']=={'<init>'} and counted[BASE+'JdbcAdmissionFailures']=={'replace'}
 init={x for x in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if x.startswith('dev/codex/schubert/nk/') and 'SchemaHistoryAdmissionTest' not in x};assert init==TARGETS;met=load(META/'manifest.json');assert met['actualExit']==0 and met['productTestsExecuted']==0 and met['execSha256']==sha(U/'jacoco.exec');actual={}
 for cl in E.parse(META/'bootstrap-methods.xml').getroot().findall('.//class'):
  methods=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
  if methods:actual[cl.get('name')]=methods
 assert set(actual)==TARGETS;assert {x['name'] for x in actual[BASE+'JdbcAdmissionFailures']}=={'replace'};javap=(META/'javap.stdout').read_text();assert re.search(r'private dev\.codex\.schubert\.nk\.api\.bootstrap\.JdbcAdmissionFailures\(\);\s*Code:\s*0: aload_0\s*1: invokespecial[^\n]*java/lang/Object\."<init>"[^\n]*\s*4: return',javap);dynamic=[x.rsplit('//',1)[-1].strip() for x in javap.splitlines() if 'InvokeDynamic' in x];assert len(dynamic)==4;assert sum('makeConcatWithConstants' in x for x in dynamic)==1;assert all(sum((':'+n+':') in x for x in dynamic)==1 for n in ['toString','hashCode','equals']);assert all(any((':'+n+':') in x for n in ['toString','hashCode','equals','makeConcatWithConstants']) for x in dynamic)
 guard=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22680-schema-source-transform-guard-v1/manifest.json';g=load(guard);assert g['actualExit']==0 and g['waitDeadlineAdditions']==2 and g['currentTestSha256']==sha(test) and g['allOtherJavaTokensAndOracleValuesUnchanged'] and g['negativeGuards']==3
 stat=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22676-schema-nine-static-applicability-v1/manifest.json';st=load(stat);assert st['inputHashes']==b['inputHashes'] and st['pmdRaw']==10 and all(st[x]==0 for x in ['applicableViolations','checkstyle','spotbugs','processingErrors']);assert all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in st['individualClassifications']);assert sha(st['staticManifest']['path'])==st['staticManifest']['sha256'];comp=RUNS/'pg22674-schema-nine-compile-v2/manifest.json';assert sha(comp)==b['compileManifestSha256'] and load(comp)['actualExit']==0 and load(comp)['inputHashes']==b['inputHashes'];assert 'task.get(5, java.util.concurrent.TimeUnit.SECONDS)' in test.read_text() and 'barrier.await(5, java.util.concurrent.TimeUnit.SECONDS)' in test.read_text()
 OUT.mkdir();files={}
 for base,prefix in [(U,'original-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file() and p.name!='jacoco.exec':
    name=prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,OUT/name);files[name]=sha(OUT/name)
 shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec');(OUT/'executed-main-methods.json').write_text(json.dumps(actual,indent=2)+'\n');files['executed-main-methods.json']=sha(OUT/'executed-main-methods.json');result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=9,newUniqueTests=0,requalifiedExistingTests=9,newSourceProofs=0,sourceQualificationMeaning='Existing HOST_COUNTERS_CLOSED baseline components requalified at changed Test; no missing-source registry credit inferred',coverage=counters,familyCoverage=familyCoverage,physical=physical,classIds=ids,rawProbes={n:probes[n] for n in ids},standardFilters=['RecordFilter generated ObjectMethods/accessors','FinallyFilter javac duplicate cleanup','PrivateEmptyNoArgConstructorFilter for noninstantiable JdbcAdmissionFailures'],manualExclusions=[],productInitializations=sorted(init),actualMainMethods=actual,realDbAdmissionRootNativeCredentialOperations=0,heldFourInitializations=0,oldExecCombined=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=environment,sourceGuard=dict(path=str(guard.relative_to(R)),sha256=sha(guard)),staticClassification=dict(path=str(stat.relative_to(R)),sha256=sha(stat)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),files=files,bugWait='BUG-2443',bugStyle='BUG-2444',yktWaitStillOpen='YKT-2177',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requalified=9,newUnique=0,line=89,method=8,classes=3,branch=78,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
