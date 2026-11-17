"""Only current Characterization Main6 and two new ordinary Tests; no application execution."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,shutil
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379/pg37300-p020-prepare-v1';out=b/'evidence/PG37300-p020-prepare-v1';assert not w.exists() and not out.exists();w.mkdir();out.mkdir();jdk=tc/'jdk-25.0.4/bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text())
main=sorted((r/'program/characterization/src/main/java').rglob('*.java'));test=[r/'program/characterization/tests/java/dev/codex/schubert/characterization'/(n+'.java') for n in ['CharacterizationIoScopeTest','GateOutputFailureContractTest']];assert len(main)==6
rows=[]
for p in main+test:
 before=p.read_bytes();cmd=[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',p.name,'-'];x=subprocess.run(cmd,input=before,capture_output=True,timeout=30);assert x.returncode==0,(p,x.stderr.decode());p.write_bytes(x.stdout);rows.append(dict(path=str(p.relative_to(r)),beforeSha256=hashlib.sha256(before).hexdigest(),afterSha256=sha(p),exit=0))
pins={str(p.relative_to(r)):sha(p) for p in main+test};stages={};env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),HOME=os.environ['HOME'],LANG='C.UTF-8')
def run(name,cmd,cwd=r,timeout=180):
 begin=dict(command=cmd,cwd=str(cwd),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(name+'.begin.json')).open('x').write(json.dumps(begin,indent=2)+'\n')
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
  child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=stdout,stderr=stderr);(out/(name+'.pid.json')).open('x').write(json.dumps(dict(pid=child.pid,command=cmd,startUTC=begin['startUTC']))+'\n')
  timed=False
  try:code=child.wait(timeout)
  except subprocess.TimeoutExpired:timed=True;child.terminate();code=child.wait(10)
 result=dict(actualExit=code,timedOut=timed,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd);(out/(name+'.exit.json')).open('x').write(json.dumps(result,indent=2)+'\n');stages[name]=result;return code
snapshot=w/'snapshot';snapshot.mkdir();paths=['pom.xml','program/characterization/pom.xml']+['src/schubert-nk-'+m+'/pom.xml' for m in ['protocol','storage','bootstrap','api','web','batch']]+[str(p.relative_to(r)) for p in main]
for name in paths:
 p=snapshot/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,p);pins[name]=sha(r/name)
mvn=tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';run('maven-main',[str(mvn),'-o','-B','-ntp','-Dmaven.repo.local='+str(tc/'m2/repository'),'-pl','program/characterization','-am','compile'],snapshot)
classes=snapshot/'program/characterization/target/classes';cfg=ld(r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/package.json');sdk=r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/sdk';cp=':'.join([str(classes),*[str(sdk/n) for n in cfg['compileSdk']]])
if stages['maven-main']['actualExit']==0:
 (w/'testclasses').mkdir();run('test-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(w/'testclasses'),*[str(p) for p in test]])
for title,paths2 in [('main',main),('test',test)]:
 run(title+'-checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/(title+'-checkstyle.xml')),*[str(p) for p in paths2]])
 filelist=w/(title+'-files.txt');filelist.write_text('\n'.join(str(p) for p in paths2)+'\n')
 run(title+'-pmd',[str(tc/'static-gates-20261015/pmd-bin-7.28.0/bin/pmd'),'check','--file-list',str(filelist),'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--format','xml','--report-file',str(out/(title+'-pmd.xml')),'--no-cache'])
result=dict(actualExit=0 if all(v['actualExit']==0 for v in stages.values()) else 1,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceBefore=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMainUnchanged='91c55386a79a59b9766fb1cc9447d7451c71c083',inputHashes=pins,format=rows,stages=stages,classes={str(p.relative_to(classes)):sha(p) for p in sorted(classes.rglob('*.class'))},productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(actualExit=result['actualExit'],stages={k:v['actualExit'] for k,v in stages.items()},physical=len(result['classes']))));raise SystemExit(result['actualExit'])
