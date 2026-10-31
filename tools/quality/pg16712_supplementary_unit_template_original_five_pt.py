"""Original whole supplementary Unit text five; only four own classpath resources, no Main jars."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SESSION='PG16712-SUPPLEMENTARY-UNIT-TEMPLATE-ORIGINAL-FIVE'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg16712-supplementary-unit-template-original-five-pt-v1'
OUT=data.BASE/'PG16712-supplementary-unit-template-original-five-pt-v1'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
TEST=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java'
TEST_SHA='3cba455dc9b66715669807d5e1408bb80059db9c07d06f7818a92930d2bd5b1a'
RESOURCES={name:'src/deployment/systemd/'+name for name in ['schubert-nk-backup.service.template','schubert-nk-bootstrap-admin.service.template','caddy.service.d/schubert-nk-startup-policy.conf','caddy.service.d/schubert-nk-stop-policy.conf']}
RUNTIME=('PG16605-application-unit-original-five-pt-v2','c4129cc8f24413764004a2422e0a153bb2341fd43641d4a08dcaa80cca0a0e2f')
NAME='dev.codex.schubert.nk.batch.platform.SupplementaryUnitTemplateTest'
def require(ok,why):
    if not ok:raise ValueError(why)
def definitions(entries,resources):
    result={}
    for resource in resources:
        found=[]
        for item in entries:
            path=Path(item)
            if path.is_dir():
                if (path/resource).is_file():found.append(str(path/resource))
            else:
                with zipfile.ZipFile(path) as jar:
                    if resource in jar.namelist():found.append(str(path)+'!/'+resource)
        require(len(found)==1,'one declared public classpath definition')
        result[resource]=found[0]
    return result
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only')
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=COMPILE/'snapshot'
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current compile-only')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'same frozen normal inputs')
    text=TEST.read_text();require(data.sha(TEST.read_bytes())==hashes[str(TEST.relative_to(data.ROOT))]==TEST_SHA,'whole original Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    require(len(methods)==len(set(methods))==text.count('@Test')==5 and not any(x in text for x in ['ProcessBuilder','DriverManager','Files.','Class.forName','Runtime.getRuntime','new Thread','getenv(']),'whole public text-only suite')
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1]);b=runtime['begin']
    require(runtime['actualExit']==0 and runtime['source']==SOURCE,'qualified library reference only')
    external=b['classpathEntries'][1:];deps=b['dependencyHashes'];excluded={r['path'] for r in normal['jars'].values()}
    require(len(external)==len(set(external)) and set(external)==set(deps) and not set(external)&excluded and all(x.endswith('.jar') and data.sha(Path(x).read_bytes())==deps[x] for x in external),'external-only unchanged runtime, no old classes or Main jars')
    agent=b['jacocoAgent'];require(data.sha(Path(agent['path']).read_bytes())==agent['sha256'],'separate fixed instrumentation agent')
    helper=data.ROOT/'tools/quality/architecture/SupplementaryUnitFiveCurrentJunitLauncher.java';reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','qualified unchanged reporter')
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir();copies={};inputs={}
    for name,path in RESOURCES.items():
        blob=(snapshot/path).read_bytes();require(data.sha(blob)==hashes[path],'four fixed public resources')
        target=classes/'systemd'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);copies[str(target)]=hashes[path];inputs[path]=hashes[path]
    entries=[str(classes),*external];resources=['systemd/'+name for name in RESOURCES];unique=definitions(entries,resources)
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=normal_pin,sourceHashes=hashes,publicResourceInputs=inputs,publicResourceCopies=copies,classpathDefinitions=unique,classpathEntries=entries,excludedProductionMainJars=sorted(excluded),dependencyHashes=deps,testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [TEST,helper,reporter]},selectedMethods=methods,selectedSuites={'SupplementaryUnitTemplateTest':5},runtimeLibraryReference=list(RUNTIME),jacocoAgent=agent,actualManagerServiceActions=0,priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin';cp=os.pathsep.join(entries)
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(TEST),str(helper),str(reporter)],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-javaagent:'+agent['path']+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],SLOT,timeout=180))
    cases=[];xmls={};suites={}
    for file in (SLOT/'xml').glob('TEST-*.xml'):
        xml=ET.parse(file).getroot();xmls[file.name]=data.sha(file.read_bytes());suites[xml.get('name')]={k:int(xml.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for c in xml.findall('testcase'):cases.append(dict(classname=c.get('classname'),name=c.get('name'),result='PASS' if not list(c) else 'NOT_PASS'))
    passed=len(stages)==2 and all(s['actualExit']==0 and not s['timedOut'] for s in stages) and len(cases)==5 and {(v['classname'],v['name']) for v in cases}=={(NAME,n) for n in methods} and all(v['result']=='PASS' for v in cases) and len(suites)==1 and all(v==dict(tests=5,failures=0,errors=0,skipped=0) for v in suites.values())
    require(definitions(entries,resources)==unique and all(data.sha(Path(p).read_bytes())==h for p,h in copies.items()) and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'unchanged exact resources/source/unique definitions')
    environment={}
    if len(stages)==2:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):k,v=line.strip().split('=',1);require(k not in environment,'one actual own JVM header');environment[k]=v
        require(len(environment)==4,'original own JVM environment')
    verify(invocation);result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=environment,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=result['tests'],suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
