"""BUG3171 corrected local only; actual failed run retained, same-source actual Main16 SB."""
from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,shutil,xml.etree.ElementTree as E
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379';old=w/'pg37312-p020-remote142-recovered';out=b/'evidence/PG37316-p020-fixture-fix-static-v1';stage=w/'pg37316-p020-fixture-fix-static-v1';assert not out.exists() and not stage.exists();out.mkdir();stage.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());jdk=tc/'jdk-25.0.4/bin';env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),HOME=os.environ['HOME'],LANG='C.UTF-8',MAVEN_OPTS='-Xmx1g -Djava.awt.headless=true')
unit=ld(old/'terminal.json');assert unit['actualExit']==1 and unit['stages']['unit']['actualExit']==1
failed=[];passed=[]
for f in (old/'xml').glob('*.xml'):
 for c in E.parse(f).getroot().findall('testcase'):
  (failed if c.find('failure') is not None or c.find('error') is not None else passed).append((c.get('classname'),c.get('name')))
assert len(passed)==141 and failed==[('dev.codex.schubert.characterization.GateOutputFailureContractTest','nestedSameOutputIsRejectedWithoutReleasingOuterClaim()')]
failure=b/'evidence/PG37314-p020-failed142-raw-observation-v1';assert not (failure/'manifest.json').exists()
for name in ['terminal.json','begin.json','jacoco.exec','coverage.xml','unit.log','execinfo.log']:shutil.copyfile(old/name,failure/name)
shutil.copytree(old/'xml',failure/'xml')
(failure/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,observedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),runActualExit=1,source=unit['source'],run='PG37312-COMMON142',success=141,failed=1,errors=0,skipped=0,notRun=0,failedCase=failed,acceptedAsPass=False,rawMeasurementsInformationalOnly=True,formalUpdated=False,newAcceptance=0,files={str(p.relative_to(failure)):sha(p) for p in failure.rglob('*') if p.is_file()}),indent=2)+'\n')
p=r/'program/characterization/tests/java/dev/codex/schubert/characterization/GateOutputFailureContractTest.java';before=subprocess.check_output(['git','show',unit['source']+':'+str(p.relative_to(r))],text=True);assert before==p.read_text().replace('ownedOutput','output')
x=subprocess.run([str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',p.name,'-'],input=p.read_bytes(),capture_output=True,timeout=30);assert x.returncode==0;p.write_bytes(x.stdout)
tokens=lambda s:re.findall(r'"(?:\\.|[^"\\])*"|\w+|\S',s);assert tokens(before)==tokens(p.read_text().replace('ownedOutput','output'))
for name in ['pom.xml','program/characterization/pom.xml',*['src/schubert-nk-'+m+'/pom.xml' for m in ['protocol','storage','bootstrap','api','web','batch']]]:
 target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,target)
for path,h in ld(old/'begin.json')['sourceHashes'].items():
 if '/src/main/java/' in path:
  assert sha(r/path)==h;target=stage/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/path,target)
classes=stage/'program/characterization/target/classes';shutil.copytree(old/'mainclasses',classes);assert {str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')}==unit['mainClasses']
cfg=ld(w/'pg37308-p020-public-package-v1/package.json');sdk=w/'pg37308-p020-public-package-v1/sdk';cp=':'.join([str(classes),*[str(sdk/n) for n in cfg['compileSdk']]]);stages={}
def run(name,cmd,cwd=r):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:x=subprocess.run(cmd,cwd=cwd,env=env,stdout=stdout,stderr=stderr,timeout=180)
 stages[name]=dict(actualExit=x.returncode,command=cmd,cwd=str(cwd),startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());return x.returncode
(stage/'testclasses').mkdir();assert run('changed-test-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(stage/'testclasses'),str(p)])==0
assert run('changed-test-checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),str(p)])==0
assert run('changed-test-pmd',[str(tc/'static-gates-20261015/pmd-bin-7.28.0/bin/pmd'),'check','-d',str(p),'--aux-classpath',cp,'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--format','xml','--report-file',str(out/'pmd.xml'),'--no-cache'])==0
assert run('actual16-spotbugs',[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','-B','-ntp','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','-Dspotbugs.effort=Max','-Dspotbugs.threshold=Low','-Dspotbugs.failOnError=true','-Dspotbugs.xmlOutput=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],stage/'program/characterization')==0
sb=stage/'program/characterization/target/spotbugsXml.xml';shutil.copyfile(sb,out/sb.name);tree=E.parse(sb).getroot();assert not tree.findall('BugInstance') and not tree.findall('.//MissingClass') and not tree.findall('.//Error');assert {v.get('class') for v in tree.findall('.//ClassStats')}=={n[:-6].replace('/','.') for n in unit['mainClasses']}
main=list(r.glob('program/characterization/src/main/java/**/*.java'));tests=[p,r/'program/characterization/tests/java/dev/codex/schubert/characterization/CharacterizationIoScopeTest.java'];v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceHashes={str(p.relative_to(r)):sha(p) for p in main+tests},mainClassHashes=unit['mainClasses'],mainSameAsFailedRun=True,all16ActualBytesSpotbugsBugsMissingErrors0=True,oldMavenVsJavacPhysicalDifference=12,reasonActualByteCheck='Both original25 compiler paths preserve all source but Maven debug options change12 physical files. Analyze actual executed16 independently rather than transfer Maven-byte SB qualification.',fix='local output renamed ownedOutput only; all Java tokens including string literals identical after inverse local name substitution',stages=stages,failedRunRetained=True,testsReexecuted=0,noOracleRelaxation=True,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,static=0,actualPhysical=16,testsExecuted=0,oldFailureRetained=True)))
