"""Original four public config-source contracts; fresh own JVM, seven closed resource copies."""
import json
import os
from pathlib import Path
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg16446-config-source-original-four-pt-v1'
OUT=data.BASE/'PG16446-config-source-original-four-pt-v1'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
TEST=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java'
TEST_SHA='59e19ad3d1ae556c476257a65795ef24b9e4f2ee38c400d4f79b196a0de42440'
NAMES=['common.yml.template','api.yml.template','web.yml.template','batch.yml.template','api.env.template','web.env.template','inbox-inspector.env.template']
SESSION='PG16446-CONFIG-SOURCE-ORIGINAL-FOUR'
RUNTIME=('PG16430-maintenance-stop-parser-eight-pt-v1','847d6fd8c22428c096c216efda4a7089abf61bdfb50716ccd100c0a15ea3bcaf')
def require(ok,why):
    if not ok:raise ValueError(why)
def definitions(entries,classes):
    result={}
    for name in NAMES:
        entry='config/'+name;locations=[]
        for raw in entries:
            path=Path(raw)
            if path.is_dir():
                if (path/entry).is_file():locations.append(raw)
            elif path.suffix=='.jar':
                with zipfile.ZipFile(path) as jar:
                    if entry in jar.namelist():locations.append(raw)
        require(locations==[str(classes)],'one own closed public resource definition');result[entry]=locations
    return result
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only own JVM')
    normal,normal_pin=cfg.normal();require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current compile-only')
    snapshot=COMPILE/'snapshot';hashes=normal['begin']['inputHashes'];require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'all frozen normal inputs')
    require(data.sha(TEST.read_bytes())==hashes[str(TEST.relative_to(data.ROOT))]==TEST_SHA,'unchanged whole original Test')
    text=TEST.read_text();methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    require(len(methods)==len(set(methods))==text.count('@Test')==4 and not any(s in text for s in ['@Before','@After','@TempDir','Files.','System.getProperty','System.getenv','ProcessBuilder','DriverManager','java.sql','java.net.','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec']),'resource text/lexical-only whole original')
    require(text.count('getResourceAsStream("/config/" + name)')==1,'closed classpath resource reader')
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1]);require(runtime['source']==SOURCE and runtime['actualExit']==0,'tool/runtime identity only, not prior PT transfer')
    dependencies=runtime['begin']['dependencyHashes'];require(all(data.sha(Path(p).read_bytes())==h for p,h in dependencies.items()),'frozen runtime libraries')
    compile_command=runtime['stages'][0]['command'];prior_entries=compile_command[compile_command.index('-cp')+1].split(os.pathsep)
    require(prior_entries[0].endswith('/pg16430-maintenance-stop-parser-eight-pt-v1/fresh-test-classes') and all(p in dependencies for p in prior_entries[1:]),'drop all old Test classes, keep only qualified library byte')
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir()
    copies={};inputs={}
    for name in NAMES:
        relative='src/deployment/config/'+name;pin=hashes[relative];blob=(snapshot/relative).read_bytes();require(data.sha(blob)==pin,'frozen public template')
        target=classes/'config'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(blob);copies[str(target)]=pin;inputs[name]=dict(path=relative,sha256=pin)
    entries=[str(classes),*prior_entries[1:]];locations=definitions(entries,classes);cp=os.pathsep.join(entries)
    helper=data.ROOT/'tools/quality/architecture/ConfigSourceFourCurrentJunitLauncher.java';reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','qualified reporter')
    agent=next(Path(p) for p in dependencies if p.endswith('org.jacoco.agent-0.8.15-runtime.jar'))
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=normal_pin,sourceHashes=hashes,publicResourceInputs=inputs,publicResourceCopies=copies,publicResourceDefinitions=locations,classpathEntries=entries,dependencyHashes=dependencies,testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [TEST,helper,reporter]},selectedMethods=methods,selectedSuites={'ConfigurationTemplateContractTest':4},runtimeLibraryReference=list(RUNTIME),priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin'
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(TEST),str(helper),str(reporter)],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],SLOT,timeout=180))
    cases=[];xmls={};suites={}
    if len(stages)==2:
        for file in (SLOT/'xml').glob('TEST-*.xml'):
            xml=ET.parse(file).getroot();xmls[file.name]=data.sha(file.read_bytes());suites[xml.get('name')]={k:int(xml.get(k,'0')) for k in ['tests','failures','errors','skipped']}
            for case in xml.findall('testcase'):cases.append(dict(classname=case.get('classname'),name=case.get('name'),result='PASS' if not list(case) else 'NOT_PASS'))
    expected={('dev.codex.schubert.nk.batch.platform.ConfigurationTemplateContractTest',n) for n in methods}
    passed=len(stages)==2 and all(v['actualExit']==0 and not v['timedOut'] for v in stages) and len(cases)==4 and {(v['classname'],v['name']) for v in cases}==expected and all(v['result']=='PASS' for v in cases) and len(suites)==1 and all(s==dict(tests=4,failures=0,errors=0,skipped=0) for s in suites.values())
    require(definitions(entries,classes)==locations and all(data.sha(Path(p).read_bytes())==h for p,h in copies.items()) and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'end unchanged inputs/copies/unique definitions')
    environment={}
    if len(stages)==2:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):key,value=line.strip().split('=',1);require(key not in environment,'unique original environment');environment[key]=value
        require(len(environment)==4,'original own JVM environment only')
    verify(invocation)
    result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=environment,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=result['tests'],suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
