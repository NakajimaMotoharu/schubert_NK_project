"""Original whole Unit contract5; isolated syntax parser only, no Production Main classpath."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SESSION='PG16605-APPLICATION-UNIT-ORIGINAL-FIVE'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg16605-application-unit-original-five-pt-v2'
OUT=data.BASE/'PG16605-application-unit-original-five-pt-v2'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
TEST=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/ApplicationServiceUnitTest.java'
TEST_SHA='6d20dd9f2ada2e1ee5a3de1ff133adb811519f2bb5d09e787d525e187597da9f'
FIXTURE=TEST.parent/'UnitSyntaxFixture.java'
FIXTURE_SHA='6f4fdc11d56ba27c72fe03c282e0551bd59ae066558fe046bc2d90f9d0919719'
TOOL=Path('/usr/bin/systemd-analyze')
TOOL_SHA='188138cf3aea2111c7744069b58c0597559808163d1b7f74ded0348d85e4bef3'
RESOURCES=['src/deployment/systemd/schubert-nk-api.service.template','src/deployment/systemd/schubert-nk-web.service.template','src/deployment/config/api.env.template','src/deployment/config/web.env.template']
RUNTIME=('PG16430-maintenance-stop-parser-eight-pt-v1','847d6fd8c22428c096c216efda4a7089abf61bdfb50716ccd100c0a15ea3bcaf')
NAME='dev.codex.schubert.nk.api.maintenance.ApplicationServiceUnitTest'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only')
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=COMPILE/'snapshot'
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current compile only')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'unchanged frozen source')
    require(data.sha(TEST.read_bytes())==hashes[str(TEST.relative_to(data.ROOT))]==TEST_SHA and data.sha(FIXTURE.read_bytes())==hashes[str(FIXTURE.relative_to(data.ROOT))]==FIXTURE_SHA,'whole Test/fixture pins')
    text=TEST.read_text();methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    require(len(methods)==len(set(methods))==text.count('@Test')==5,'five original methods')
    require(text.count('new ProcessBuilder(')==2 and text.count('"/usr/bin/systemd-analyze"')==2 and text.count('"verify"')==2 and text.count('process.environment().clear()')==2 and text.count('UnitSyntaxFixture.environment(directory)')==2 and not any(v in text for v in ['systemctl','DriverManager','java.sql','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec']),'closed reviewed parser operations, not arbitrary command')
    require(data.sha(TOOL.read_bytes())==TOOL_SHA,'fixed public parser tool')
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1]);require(runtime['source']==SOURCE and runtime['actualExit']==0,'reused library bytes only')
    deps=runtime['begin']['dependencyHashes'];require(all(data.sha(Path(p).read_bytes())==h for p,h in deps.items()),'runtime bytes')
    compile_command=runtime['stages'][0]['command'];entries=compile_command[compile_command.index('-cp')+1].split(os.pathsep)
    require(entries[0].endswith('/pg16430-maintenance-stop-parser-eight-pt-v1/fresh-test-classes') and all(v in deps for v in entries[1:]),'exclude old Test classpath')
    main_jars={row['path'] for row in normal['jars'].values()}
    external=[v for v in entries[1:] if v not in main_jars]
    require(len(external)==len(set(external)) and all(v.endswith('.jar') and not '/dev/codex/' in v and v in deps for v in external) and not set(external)&main_jars,'external-only dependencies, no Product Main jars')
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir();repo=SLOT/'public-repository';repo.mkdir()
    copies={};inputs={}
    for path in RESOURCES:
        blob=(snapshot/path).read_bytes();require(data.sha(blob)==hashes[path],'fixed public resource')
        target=repo/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);copies[str(target)]=hashes[path];inputs[path]=hashes[path]
    helper=data.ROOT/'tools/quality/architecture/ApplicationUnitFiveCurrentJunitLauncher.java';reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','qualified reporter')
    cp=os.pathsep.join([str(classes),*external]);agent=next(Path(p) for p in deps if p.endswith('org.jacoco.agent-0.8.15-runtime.jar'))
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=normal_pin,sourceHashes=hashes,publicRepository=str(repo),publicResourceInputs=inputs,publicResourceCopies=copies,classpathEntries=[str(classes),*external],excludedProductionMainJars=sorted(main_jars),dependencyHashes={v:deps[v] for v in external},testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [TEST,FIXTURE,helper,reporter]},selectedMethods=methods,selectedSuites={'ApplicationServiceUnitTest':5},runtimeLibraryReference=list(RUNTIME),syntaxTool=dict(path=str(TOOL),sha256=TOOL_SHA),jacocoAgent=dict(path=str(agent),sha256=deps[str(agent)]),ownSyntaxParserInvocationsDeclared=3,actualManagerServiceActions=0,priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin'
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(TEST),str(FIXTURE),str(helper),str(reporter)],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('syntax-tool-version',[str(TOOL),'--version'],SLOT,timeout=10))
    if len(stages)==2 and stages[1]['actualExit']==0 and not stages[1]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Dnk.pt.repository='+str(repo),'-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],SLOT,timeout=180))
    cases=[];xmls={};suites={}
    if len(stages)==3:
        for file in (SLOT/'xml').glob('TEST-*.xml'):
            xml=ET.parse(file).getroot();xmls[file.name]=data.sha(file.read_bytes());suites[xml.get('name')]={k:int(xml.get(k,'0')) for k in ['tests','failures','errors','skipped']}
            for case in xml.findall('testcase'):cases.append(dict(classname=case.get('classname'),name=case.get('name'),result='PASS' if not list(case) else 'NOT_PASS'))
    expected={(NAME,n) for n in methods}
    passed=len(stages)==3 and all(v['actualExit']==0 and not v['timedOut'] for v in stages) and len(cases)==5 and {(v['classname'],v['name']) for v in cases}==expected and all(v['result']=='PASS' for v in cases) and len(suites)==1 and all(v==dict(tests=5,failures=0,errors=0,skipped=0) for v in suites.values())
    require(all(data.sha(Path(p).read_bytes())==h for p,h in copies.items()) and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()) and data.sha(TOOL.read_bytes())==TOOL_SHA,'unchanged input/tool/copy')
    require({str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file()}==set(RESOURCES),'exact four public repository copies')
    environment={}
    if len(stages)==3:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):key,value=line.strip().split('=',1);require(key not in environment,'unique original environment');environment[key]=value
        require(len(environment)==4,'actual original JVM environment')
    verify(invocation)
    result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=environment,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=result['tests'],suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
