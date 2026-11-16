"""Collect unchanged original static policies on all five common Main and ten current classfiles."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379';unit=w/'pg37012-p020-remote124-recovered'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());old=b/'evidence/PG36938-ssc450-all162-static-v1'
out=b/'evidence/PG37018-p020-five-main-static-v1';assert not out.exists();out.mkdir()
stage=w/'pg37018-p020-five-main-static-v1';assert not stage.exists();stage.mkdir(mode=0o700)
for path in ['pom.xml','program/characterization/pom.xml',*[f'src/schubert-nk-{x}/pom.xml' for x in ['protocol','storage','bootstrap','api','web','batch']]]:
 p=stage/path;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/path,p)
shutil.copytree(unit/'mainclasses',stage/'program/characterization/target/classes')
files=sorted(r.glob('program/characterization/src/main/java/**/*.java'));assert len(files)==5
for p in files:
 target=stage/p.relative_to(r);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
(out/'sources.txt').write_text(''.join(str(p)+'\n' for p in files))
args={}
args['format']=load(old/'format-begin.safe.json')['command'][:6]+[str(p) for p in files]
base=load(old/'checkstyle-begin.safe.json')['command'];args['checkstyle']=base[:8]+[str(out/'checkstyle.xml')]+[str(p) for p in files]
base=load(old/'pmd-begin.safe.json')['command'];base=list(base)
for flag,val in [('--file-list',str(out/'sources.txt')),('--aux-classpath',':'.join([str(tc/'jdk-25.0.4/lib/jrt-fs.jar'),str(unit/'mainclasses'),*[str(w/'pg37008-p020-public-package-v1/sdk'/n) for n in load(w/'pg37008-p020-public-package-v1/package.json')['compileSdk']]])),('--report-file',str(out/'pmd.xml'))]:base[base.index(flag)+1]=val
args['pmd']=base
args['spotbugs']=[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','-Dspotbugs.effort=Max','-Dspotbugs.threshold=Low','-Dspotbugs.failOnError=true','-Dspotbugs.xmlOutput=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']
env=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),MAVEN_USER_HOME=str(tc/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')
stages={}
for name,cmd in args.items():
 cwd=stage/'program/characterization' if name=='spotbugs' else r
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
  child=subprocess.run(cmd,cwd=cwd,env=env,stdout=stdout,stderr=stderr,timeout=180)
 stages[name]=dict(actualExit=child.returncode,command=cmd,cwd=str(cwd),startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
 print(json.dumps(dict(stage=name,actualExit=child.returncode)),flush=True)
 sb=list((stage/'program/characterization/target').glob('spotbugs*.xml')) if name=='spotbugs' else []
 for p in sb:shutil.copyfile(p,out/p.name)
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9',actualUnitSource='1f5ea8f143a8465fd67fd1b78131b4c5052e59ff',stages=stages,sourceHashes={str(p.relative_to(r)):sha(p) for p in files},classHashes=load(unit/'terminal.json')['mainClasses'],rawCollectionOnly=True,qualityAccepted=False,noNewSuppressions=True,noRulesChanged=True,files={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name != 'manifest.json'}),ensure_ascii=False,indent=2)+'\n')
for name in ['checkstyle','pmd']:
 root=ET.parse(out/(name+'.xml')).getroot();print(name,'issues',sum(len(x) for x in root.findall('.//file')))
