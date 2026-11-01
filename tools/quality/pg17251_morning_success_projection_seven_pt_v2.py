"""Whole original7 successful-Backup projection through its original unchanged fake-JDBC Probe; no actual DB."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17251-morning-success-projection-seven-pt-v2'
OUT=data.BASE/'PG17251-morning-success-projection-seven-pt-v2'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
TEST_PATHS={'dev.codex.schubert.nk.batch.repository.MorningSuccessfulBackupProjectionTest':('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningSuccessfulBackupProjectionTest.java',7)}
EXTRA_TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
POMS=[]
SESSION='PG17251-MORNING-SUCCESS-PROJECTION-ORIGINAL7-V2'
RUNTIME=('PG17216-bootstrap-credential-values-twenty-pt-v1','57c0aeeab750d8a6018dfea56c83cf2f82e4d620fbde731bdee1fef79674e8c3')
def require(ok, why):
    if not ok: raise ValueError(why)
def projection_guard(text):
    return 'MorningDatabaseSessionTest.Probe' in text and not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','System.getenv','Files.write','Files.delete','java.net','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only own JVM')
    normal,pin=cfg.normal();snapshot=COMPILE/'snapshot';hashes=normal['begin']['inputHashes']
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'normal compile only')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'all frozen inputs')
    prior=data.read_checked(data.BASE/'PG17236-current2643-runtime-pom-registry-v1/manifest.json','25d0c1833db48ab5ec38ab0d0a9ad9799b53db0c7823c081d575b0207461d754')
    require(not set(TEST_PATHS)&set(prior['suiteNames']),'no completed current suite replay')
    methods={};test_files=[]
    for binary,(path,count) in TEST_PATHS.items():
        file=data.ROOT/path;text=file.read_text();test_files.append(file)
        require(data.sha(file.read_bytes())==hashes[path],'whole original Test')
        names=re.findall(r'@Test\s+void\s+(\w+)\(',text)
        require(len(names)==len(set(names))==text.count('@Test')==count,'whole original methods')
        require(projection_guard(text), 'whole original7 pure JDBC proxy, not actual connection')
        require(set(re.findall(r'java\.sql\.\w+',text))=={'java.sql.SQLException'},'only explicitly reviewed SQL exception type')
        bads=[text+'\\n'+v for v in ['DriverManager.getConnection(', 'Files.write(', 'System.getenv(', '@BeforeAll', 'java.net.Socket']]
        require(all(not projection_guard(v) for v in bads) and not projection_guard(''),'finite nondegenerate safety boundaries')
        require(text.count('Files.readString(')==text.count('System.getProperty("nk.pt.repository")')==0 and 'MorningDatabaseSessionTest.Probe' in text,'whole original fake JDBC test, no IO')
        methods[binary]=names
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1])
    require(runtime['source']==SOURCE and runtime['actualExit']==0,'runtime library reference only')
    deps=runtime['begin']['dependencyHashes'];require(all(data.sha(Path(p).read_bytes())==h for p,h in deps.items()),'fixed dependencies')
    command=runtime['stages'][0]['command'];entries=command[command.index('-cp')+1].split(os.pathsep)
    require(entries[0].endswith('/pg17216-bootstrap-credential-values-twenty-pt-v1/fresh-test-classes') and all(p in deps for p in entries[1:]),'drop old Test classes')
    helper=data.ROOT/'tools/quality/architecture/MorningSuccessProjectionSevenCurrentJunitLauncher.java'
    reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','reporter identity')
    extra=data.ROOT/EXTRA_TEST
    require(data.sha(extra.read_bytes())==hashes[EXTRA_TEST]=='cbd25ed83c772a66a3990811105c201215863fb9db27c2294cbf25f83da84009','unchanged complete original helper Test')
    require('@BeforeAll' in extra.read_text() and len(TEST_PATHS)==1 and not any(b.endswith('.MorningDatabaseSessionTest') for b in TEST_PATHS),'outer DB Test never selected, no extraction')
    test_files.append(extra)
    batch_cp=snapshot/'src/schubert-nk-batch/target/pgpt-test-classpath.txt'
    extra_libraries=[p for p in batch_cp.read_text().strip().split(os.pathsep) if p.startswith(str(runner.TC/'m2/repository')+'/')]
    require(extra_libraries and all(Path(p).is_file() for p in extra_libraries),'normal batch external libraries only')
    deps=dict(deps)
    for p in extra_libraries:
        deps[p]=data.sha(Path(p).read_bytes())
    entries=list(dict.fromkeys([*entries,*extra_libraries]))
    source_dirs=[snapshot/('src/schubert-nk-'+n+'/src/test/java') for n in normal['jars']]
    require(all(p.is_dir() for p in source_dirs),'frozen original Test source path, no Main sources')
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir()
    cp=os.pathsep.join([str(classes),*entries[1:]])
    agent=next(p for p in deps if p.endswith('org.jacoco.agent-0.8.15-runtime.jar'))
    inputs={p:hashes[p] for p in POMS}
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=pin,sourceHashes=hashes,reviewedWholeHelperInputs={EXTRA_TEST:hashes[EXTRA_TEST]},unusedPublicPomInputs=inputs,readOnlySnapshot=str(snapshot),normalBatchClasspathFileSha256=data.sha(batch_cp.read_bytes()),originalTestSourcePathDirectories=[str(p) for p in source_dirs],dependencyHashes=deps,testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [*test_files,helper,reporter]},selectedMethods=methods,selectedSuites={b:n for b,(_,n) in TEST_PATHS.items()},runtimeLibraryReference=list(RUNTIME),priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin'
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','--source-path',os.pathsep.join(map(str,source_dirs)),'-cp',cp,'-d',str(classes),*[str(p) for p in [*test_files,helper,reporter]]],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-javaagent:'+agent+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],SLOT,timeout=180))
    cases=[];xmls={};suites={}
    if len(stages)==2:
        for file in (SLOT/'xml').glob('TEST-*.xml'):
            xml=ET.parse(file).getroot();xmls[file.name]=data.sha(file.read_bytes());suites[xml.get('name')]={k:int(xml.get(k,'0')) for k in ['tests','failures','errors','skipped']}
            for c in xml.findall('testcase'):cases.append(dict(classname=c.get('classname'),name=c.get('name'),result='PASS' if not list(c) else 'NOT_PASS'))
    expected={(b,n) for b,names in methods.items() for n in names}
    passed=len(stages)==2 and all(s['actualExit']==0 and not s['timedOut'] for s in stages) and len(cases)==7 and {(c['classname'],c['name']) for c in cases}==expected and all(c['result']=='PASS' for c in cases) and set(suites)==set(TEST_PATHS) and all(suites[b]==dict(tests=n,failures=0,errors=0,skipped=0) for b,(_,n) in TEST_PATHS.items())
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'all original inputs remain')
    require(all(data.sha(Path(p).read_bytes())==h for p,h in {**deps,**begin['testSourceHashes']}.items()),'tools and runtime unchanged')
    environment={}
    if len(stages)==2:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):
                    k,v=line.strip().split('=',1);require(k not in environment,'unique original env');environment[k]=v
        require(len(environment)==4,'original own JVM environment')
    verify(invocation)
    result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=environment,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,originalOuterDbTestSelected=False,guardNegativeVectors=6,bugs=['BUG2198'],horizontal=['YKT1945'],helperCompilationOnlyBeforeSelectedWholeTest=True,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=len(cases),suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
