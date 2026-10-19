"""Independent protocol-only PT and separate static analysis; no VM/DB/service or refused PT."""
import hashlib
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,TC,sha,utc,test_names

SLOT='pg5724-semantic-enum-protocol-v1'
BASE='6db56feeea6df0e355c018e6b80ad4e40c2d90f5'


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('freeze clean committed input')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    os.umask(0o077);out=ROOT.parent/'pgpt-runs/PG379'/SLOT;out.mkdir(mode=0o700);archive=out/'source.tar'
    with archive.open('xb')as f:subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','tools/quality/static'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
    source=out/'source';source.mkdir()
    with tarfile.open(archive)as f:f.extractall(source,filter='data')
    module=source/'src/schubert-nk-protocol';target=module/'target'
    expected={p.relative_to(module/'src/test/java').as_posix()[:-5].replace('/','.'):test_names(p)for p in(module/'src/test/java').rglob('*Test.java')}
    if sum(map(len,expected.values()))!=88 or len(expected)!=18:raise ValueError('original86/17 plus explicit two compatibility tests/one suite')
    inputs={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()}
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'),PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    base=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-B','-o','-ntp','-Dmaven.repo.local='+str(TC/'m2/repository'),'-pl','src/schubert-nk-protocol']
    commands=[base+['spotless:check'],base+['package','org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    started=utc();exits=[]
    with(out/'begin.safe.json').open('x')as f:json.dump({'source':head,'archiveSha256':sha(archive),'startedUTC':started,'commands':commands,'expectedTests':88,'replayAllowed':False},f,sort_keys=True)
    for i,command in enumerate(commands,1):
        with(out/f'phase-{i}.private.log').open('xb')as f:
            p=subprocess.Popen(command,cwd=source,env=env,stdout=f,stderr=f,umask=0o027);proc=Path('/proc')/str(p.pid)
            with(out/f'phase-{i}.owner.safe.json').open('x')as m:json.dump({'pid':p.pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()},m,sort_keys=True)
            exits.append(p.wait());f.flush();os.fsync(f.fileno())
        if exits[-1]:break
    actual={};failures=[];xmls={}
    for path in(target/'surefire-reports').glob('TEST-*.xml'):
        tree=ET.parse(path).getroot();name=tree.get('name');actual[name]=set();xmls[name]=sha(path)
        for c in tree.findall('testcase'):
            method=c.get('name','').removesuffix('()');actual[name].add(method)
            if any(n.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in c.iter()):failures.append([name,method])
    coverage_path=target/'site/jacoco/jacoco.xml';coverage={};static=None
    if coverage_path.exists():coverage={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in ET.parse(coverage_path).getroot().findall('counter')}
    if(target/'spotbugsXml.xml').exists():static=len(ET.parse(target/'spotbugsXml.xml').getroot().findall('BugInstance'))
    fixed=all(sha(source/n)==h for n,h in inputs.items())
    physical={p.relative_to(target/'classes').as_posix():sha(p)for p in(target/'classes').rglob('*.class')}
    quality=fixed and exits==[0,0]and actual==expected and not failures and static==0 and len(physical)==174 and all(coverage.get(k,{}).get('missed')==0 for k in('LINE','METHOD','CLASS','BRANCH'))
    value={'source':head,'baseSource':BASE,'actualExit':next((e for e in exits if e),0),'startedUTC':started,'completedUTC':utc(),'phaseExits':exits,'tests':sum(map(len,actual.values())),'suites':len(actual),'exactInventory':actual==expected,'failedOrSkipped':failures,'sourceFixed':fixed,'staticIssues':static,'coverage':coverage,'coverageXmlSha256':sha(coverage_path)if coverage_path.exists()else None,'xmlHashes':xmls,'allPhysicalProtocolMainSha256':physical,'protocolFour100Qualified':quality,'archiveSha256':sha(archive),'vmActions':0,'refusedPtRetried':False,'ptAlternativeCompleted':0,'formalAccepted':False,'fullRegressionPending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in('xmlHashes','allPhysicalProtocolMainSha256')},sort_keys=True))
    return 0 if quality else 1


if __name__=='__main__':raise SystemExit(main())
