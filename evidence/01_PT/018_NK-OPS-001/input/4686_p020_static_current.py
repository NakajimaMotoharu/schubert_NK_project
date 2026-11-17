"""Reuse unchanged Main compile, refresh changed new-Test static and full class-complete SB."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,shutil
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379/pg37300-p020-prepare-v1';out=b/'evidence/PG37302-p020-static-current-v1';assert not out.exists();out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());old=ld(b/'evidence/PG37300-p020-prepare-v1/manifest.json');assert old['stages']['maven-main']['actualExit']==0
main=sorted(r.glob('program/characterization/src/main/java/**/*.java'));tests=[r/'program/characterization/tests/java/dev/codex/schubert/characterization'/(n+'.java') for n in ['CharacterizationIoScopeTest','GateOutputFailureContractTest']];assert all(sha(p)==old['inputHashes'][str(p.relative_to(r))] for p in main)
jdk=tc/'jdk-25.0.4/bin';stages={};env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),HOME=os.environ['HOME'],LANG='C.UTF-8',MAVEN_OPTS='-Xmx1g -Djava.awt.headless=true')
for p in tests:
 x=subprocess.run([str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',p.name,'-'],input=p.read_bytes(),capture_output=True,timeout=30);assert x.returncode==0;p.write_bytes(x.stdout)
snapshot=w/'snapshot';classes=snapshot/'program/characterization/target/classes';cfg=ld(r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/package.json');sdk=r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/sdk';cp=':'.join([str(classes),*[str(sdk/n) for n in cfg['compileSdk']]])
def run(name,cmd,cwd=r):
 begin=dict(command=cmd,cwd=str(cwd),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(name+'.begin.json')).open('x').write(json.dumps(begin,indent=2)+'\n')
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:child=subprocess.run(cmd,cwd=cwd,env=env,stdout=stdout,stderr=stderr,timeout=180)
 stages[name]=dict(actualExit=child.returncode,**begin,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(name+'.exit.json')).open('x').write(json.dumps(stages[name],indent=2)+'\n')
run('test-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(w/'testclasses'),*[str(p) for p in tests]])
run('test-checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'test-checkstyle.xml'),*[str(p) for p in tests]])
files=out/'test-files.txt';files.write_text('\n'.join(str(p) for p in tests)+'\n')
run('test-pmd',[str(tc/'static-gates-20261015/pmd-bin-7.28.0/bin/pmd'),'check','--file-list',str(files),'--aux-classpath',cp,'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--format','xml','--report-file',str(out/'test-pmd.xml'),'--no-cache'])
run('spotbugs',[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','-B','-ntp','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','-Dspotbugs.effort=Max','-Dspotbugs.threshold=Low','-Dspotbugs.failOnError=true','-Dspotbugs.xmlOutput=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot/'program/characterization')
for p in (snapshot/'program/characterization/target').glob('spotbugs*.xml'):shutil.copyfile(p,out/p.name)
result=dict(actualExit=0 if all(x['actualExit'] in ([0,4] if name=='test-pmd' else [0]) for name,x in stages.items()) else 1,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rawCollectionOnly=True,qualityAccepted=False,mainCompileReused=True,mainProofSha256=sha(b/'evidence/PG37300-p020-prepare-v1/manifest.json'),inputHashes={str(p.relative_to(r)):sha(p) for p in main+tests},physicalClassHashes={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},stages=stages)
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(actualExit=result['actualExit'],stages={k:v['actualExit'] for k,v in stages.items()})));raise SystemExit(result['actualExit'])
