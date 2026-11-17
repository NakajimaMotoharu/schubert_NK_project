"""Original compiler/NullAway flags, only admitted API parser and existing three dependency modules."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,shutil,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'));import pgpt_closed_host_profile as policy
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379/pg37342-request-details-prepare-v1';out=b/'evidence/PG37342-request-details-prepare-v1';assert not w.exists() and not out.exists();w.mkdir();out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();snapshot=w/'snapshot';snapshot.mkdir();jdk=tc/'jdk-25.0.4/bin';env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),HOME=os.environ['HOME'],LANG='C.UTF-8',MAVEN_OPTS='-Xmx1g -Djava.awt.headless=true')
main=[p for module in ['protocol','storage','bootstrap'] for p in sorted((r/('src/schubert-nk-'+module)/'src/main/java').rglob('*.java'))];target=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/RequestLogDetails.java';package=target.with_name('package-info.java');main.extend([target,package]);tests=[r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/logging'/(n+'.java') for n in ['RequestLogDetailsTest','RequestLogDetailsRawContractTest']];original=ld(b/'evidence/PG37340-request-details-source-before-v1/manifest.json');assert sha(tests[0])==original['originalTestSha256'];pins={}
paths=['pom.xml','program/characterization/pom.xml',*['src/schubert-nk-'+m+'/pom.xml' for m in ['protocol','storage','bootstrap','api','web','batch']],*[str(p.relative_to(r)) for p in main]]
for name in paths:
 policy.relative_name(name);p=r/name;raw=p.read_bytes();assert subprocess.check_output(['git','show',source+':'+name])==raw;dest=snapshot/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);pins[name]=sha(p)
stages={}
def run(name,cmd,cwd=r):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/(name+'.begin.json')).open('x').write(json.dumps(dict(command=cmd,cwd=str(cwd),source=source,startUTC=start),indent=2)+'\n')
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
  child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=stdout,stderr=stderr);(out/(name+'.pid.json')).open('x').write(json.dumps(dict(pid=child.pid,source=source,startUTC=start))+'\n');timed=False
  try:code=child.wait(180)
  except subprocess.TimeoutExpired:timed=True;child.terminate();code=child.wait(10)
 stages[name]=dict(actualExit=code,timedOut=timed,command=cmd,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(name+'.exit.json')).open('x').write(json.dumps(stages[name],indent=2)+'\n');return code
mvn=tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';run('main-compile',[str(mvn),'-o','-B','-ntp','-Dmaven.repo.local='+str(tc/'m2/repository'),'-pl','src/schubert-nk-api','-am','compile'],snapshot)
modules=['protocol','storage','bootstrap','api'];classdirs={m:snapshot/('src/schubert-nk-'+m)/'target/classes' for m in modules};jarpaths=[tc/'m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar',tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',tc/'m2/repository/com/google/errorprone/error_prone_annotations/2.45.0/error_prone_annotations-2.45.0.jar',tc/'junit-platform-console-standalone-1.13.4.jar'];jarpaths=[p for p in jarpaths if p.exists()];cp=':'.join([*[str(p) for p in classdirs.values()],*[str(p) for p in jarpaths]])
if stages['main-compile']['actualExit']==0:
 (w/'testclasses').mkdir();run('test-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(w/'testclasses'),*[str(p) for p in tests]])
for title,files in [('main',[target]),('test',[tests[1]])]:
 run(title+'-checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/(title+'-checkstyle.xml')),*[str(p) for p in files]])
 run(title+'-pmd',[str(tc/'static-gates-20261015/pmd-bin-7.28.0/bin/pmd'),'check','-d',','.join(str(p) for p in files),'--aux-classpath',cp,'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--format','xml','--report-file',str(out/(title+'-pmd.xml')),'--no-cache'])
if stages['main-compile']['actualExit']==0:
 run('spotbugs',[str(mvn),'-o','-B','-ntp','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot/'src/schubert-nk-api')
 for p in (snapshot/'src/schubert-nk-api/target').glob('spotbugs*.xml'):shutil.copyfile(p,out/p.name)
physical={m:{str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*.class'))} for m,root in classdirs.items()}
for module,files in physical.items():
 for name in files:policy.relative_name(name)
assert not list(snapshot.rglob('surefire-reports')) and all(sha(r/name)==h for name,h in pins.items())
v=dict(actualExit=0 if all(x['actualExit'] in ([0,4] if name.endswith('-pmd') else [0]) for name,x in stages.items()) and 'spotbugs' in stages else 1,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain=source,inputHashes=pins,mainSourceCount=len(main),apiSourcesExactly=[str(target.relative_to(r)),str(package.relative_to(r))],testSourceHashes={str(p.relative_to(r)):sha(p) for p in tests},stages=stages,physicalClassHashes=physical,jars={str(p):sha(p) for p in jarpaths},classPath=cp,actualProductTests=0,heldFourClassfileActions=0,originalPomsAndNullAwayFlagsUnmodified=True,wholeSixModuleGate=False,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],source=source,stages={k:v['actualExit'] for k,v in stages.items()},mainCount=len(main),physical={k:len(v) for k,v in physical.items()})));raise SystemExit(v['actualExit'])
