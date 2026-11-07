"""Independent public value-class evidence; no Root/outer reader invocation and no old exec reuse."""
from pathlib import Path
import collections,datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22626-release-contents-eight-unit-v1';META=RUNS/'pg22628-release-contents-passive-metadata-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22630-release-contents-value-independent-v1';SOURCE='71e48481b1b79366a83e400409ecf28994a3ed29';CORE='7aed8eace7c844c2f79f2e39db766faf914890d5';TARGET='dev/codex/schubert/nk/bootstrap/StartupReleaseManifest$Contents';ROW='dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission$Row';TEST='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/StartupReleaseContentsValueTest.java'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 value=0
 for byte in data:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
def main():
 assert not OUT.exists();m=load(U/'manifest.json');b=load(U/'begin.json');assert m['begin']==b and (b['source'],b['normalSource'])==(SOURCE,CORE);assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,8,0,0,0) and b['expectedTests']==b['newMethods']==8
 for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+p],cwd=R)).hexdigest()
 for p,h in b['dependencies'].items():assert sha(p)==h
 for label,s in m['stages'].items():
  assert s['actualExit']==0 and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==s[stream+'Sha256']
 assert load(U/'unit-exit.safe.json')==m['stages']['unit'];cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and cmd[-1]=='dev.codex.schubert.nk.bootstrap.StartupReleaseContentsValueTest' and '--select-method' not in cmd and '--scan-classpath' not in cmd;assert b['parentWholeQualified'] is False
 expected={('dev.codex.schubert.nk.bootstrap.StartupReleaseContentsValueTest',n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/TEST).read_text())};assert len(expected)==8;cases=[];environment={}
 for p in sorted((U/'xml').glob('TEST-*.xml')):
  t=E.parse(p).getroot();assert not any(t.findall('.//'+n) for n in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in t.findall('testcase'))
  for x in t.findall('./properties/property'):
   if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:environment[x.get('name')]=x.get('value')
 assert len(cases)==len(set(cases))==8 and set(cases)==expected
 for s in ['8 tests found','8 tests started','8 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert s in (U/'unit.stdout').read_text()
 n=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert n['source']==CORE and n['actualExit']==0
 with zipfile.ZipFile(n['jars']['bootstrap']['path']) as jar:data=jar.read(TARGET+'.class')
 assert m['physical']=={TARGET:hashlib.sha256(data).hexdigest()} and sha(U/'component'/(TARGET+'.class'))==m['physical'][TARGET];crc=crc64(data);ids={name:h for h,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert ids=={TARGET:crc}
 ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22626-RELEASE-CONTENTS8"' in ex;probes={name:(h,int(hit),int(total)) for h,hit,total,name in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};assert probes[TARGET]==(crc,16,19)
 tree=E.parse(U/'coverage.xml').getroot();classes=tree.findall('.//class');assert len(classes)==1 and classes[0].get('name')==TARGET;counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')};assert all(x['missed']==0 for x in counters.values());assert {k:counters[k]['covered'] for k in ['LINE','METHOD','CLASS']}==dict(LINE=16,METHOD=7,CLASS=1) and 'BRANCH' not in counters
 methods={(x.get('name'),x.get('desc')) for x in classes[0].findall('method')};assert methods=={('<init>','(Ljava/lang/String;Ljava/lang/String;Ljava/util/List;Ljava/util/Map;Ljava/util/Map;)V'),('<init>','(Ljava/lang/String;Ljava/lang/String;Ljava/util/List;Ljava/util/Map;Ljava/util/Map;Ljava/util/Map;Ljava/util/Map;)V'),('migrations','()Ljava/util/List;'),*[(x,'()Ljava/util/Map;') for x in ['build','platform','versions','artifactHashes']]}
 init={x for x in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if x.startswith('dev/codex/schubert/nk/') and 'StartupReleaseContentsValueTest' not in x};assert init=={TARGET,ROW};assert TARGET.removesuffix('$Contents') not in init and ROW.removesuffix('$Row') not in init
 met=load(META/'manifest.json');assert met['actualExit']==0 and met['productTestsExecuted']==0 and met['execSha256']==sha(U/'jacoco.exec');actual={}
 for cl in E.parse(META/'bootstrap-methods.xml').getroot().findall('.//class'):
  ms=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
  if ms:actual[cl.get('name')]=ms
 assert set(actual)=={TARGET,ROW} and {x['name'] for x in actual[ROW]}=={'<init>'};javap=(META/'javap.stdout').read_text()
 # JDK-generated Record ObjectMethods are recognized by JaCoCo's standard record filter.
 for signature in ['public final java.lang.String toString();','public final int hashCode();','public final boolean equals(java.lang.Object);']:assert signature in javap
 assert javap.count('InvokeDynamic')==3 and all(x not in methods for x in [('toString','()Ljava/lang/String;'),('hashCode','()I'),('equals','(Ljava/lang/Object;)Z')]);assert 'goto' not in javap and ' if' not in javap
 stat=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22634-release-contents-static-applicability-v1/manifest.json';st=load(stat);assert st['inputHashes']==b['inputHashes'] and st['pmdRaw']==4 and all(st[k]==0 for k in ['applicableViolations','checkstyle','spotbugs','processingErrors']);assert all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in st['individualClassifications']);assert sha(st['staticManifest']['path'])==st['staticManifest']['sha256']
 comp=RUNS/'pg22632-release-contents-eight-compile-v2/manifest.json';assert sha(comp)==b['compileManifestSha256'] and load(comp)['actualExit']==0;assert load(comp)['inputHashes']==b['inputHashes'];source=(R/TEST).read_text();assert 'jobs.get(index).get(5, TimeUnit.SECONDS)' in source and 'original.put(KEY_COMMIT, "changed")' in source;assert 'Class.forName' not in source and 'setAccessible' not in source and 'StartupReleaseManifest.create' not in source;assert sum(x.startswith('contents00') for x in re.findall(r'@Test\s+void\s+(\w+)\s*\(',source))==8
 OUT.mkdir();files={}
 for base,prefix in [(U,'original-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file() and p.name!='jacoco.exec':
    name=prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,OUT/name);files[name]=sha(OUT/name)
 shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec');(OUT/'executed-main-methods.json').write_text(json.dumps(actual,indent=2)+'\n');files['executed-main-methods.json']=sha(OUT/'executed-main-methods.json');result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=8,newUniqueTests=8,newSourceProofs=0,parentWholeQualified=False,newQualifiedNestedValueTypes=1,coverage=counters,branchApplicable=False,branchCovered=0,branchMissed=0,branchRatio=None,branchReason='No conditional bytecode in this value class',physical=m['physical'],classId=crc,rawProbe=dict(covered=16,total=19),standardRecordFilter=dict(generated=['toString','hashCode','equals','version accessor','sha256 accessor'],customMethodsAllMeasured=7,manualExclusions=[]),productInitializations=sorted(init),actualMainMethods=actual,outerReaderInitialized=False,heldFourInitializations=0,realRootDbNativeCredentialOperations=0,supportRowQualifiedAsWhole=False,oldExecCombined=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=environment,staticClassification=dict(path=str(stat.relative_to(R)),sha256=sha(stat)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newUnique=8,valueType=1,parentWhole=0,coverage='L16/M7/C1 missed0; branch N/A',manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
