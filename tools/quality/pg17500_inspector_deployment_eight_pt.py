"""Whole original Inspector deployment eight; owned tools and empty-environment child CLI guard only."""
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
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17500-inspector-deployment-eight-pt-v1'
OUT=data.BASE/'PG17500-inspector-deployment-eight-pt-v1'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
TEST_PATHS={'dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest':('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDeploymentTest.java',8)}
PUBLIC_FILES=['src/deployment/operations/inbox-inspector.sh.template','src/deployment/systemd/schubert-nk-inbox-inspector.service','src/deployment/systemd/optional/inbox-inspector-context-previous.conf','src/deployment/systemd/optional/inbox-inspector-response-previous.conf','src/schubert-nk-api/pom.xml']
EXTRAS=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/UnitSyntaxFixture.java']
CHILD_GUARD_FILES=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorLauncher.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorLaunchConfiguration.java','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminal.java','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.java']
TOOLS={'/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck':'311de5f94ecea1d98052ccdc94166591dce89e031e7357debd2f3213b547f7df','/usr/bin/systemd-analyze':'188138cf3aea2111c7744069b58c0597559808163d1b7f74ded0348d85e4bef3','/bin/sh':'c626229526bb58ec2d0f585f3c3ae1412e6f973b4353385042d11c38d8426917','/usr/bin/od':'f84e76ea4da1e0c4e92254bd0d7dccdabe2c8b3098e734f27997dae3ee5d8e02','/bin/cat':'f84e76ea4da1e0c4e92254bd0d7dccdabe2c8b3098e734f27997dae3ee5d8e02'}
SESSION='PG17500-INSPECTOR-DEPLOYMENT-ORIGINAL8'
RUNTIME=('PG17216-bootstrap-credential-values-twenty-pt-v1','57c0aeeab750d8a6018dfea56c83cf2f82e4d620fbde731bdee1fef79674e8c3')
def require(ok, why):
    if not ok: raise ValueError(why)
def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only own JVM')
    normal,pin=cfg.normal();snapshot=COMPILE/'snapshot';hashes=normal['begin']['inputHashes']
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'normal compile only')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'all frozen inputs')
    prior=data.read_checked(data.BASE/'PG17488-current2738-expiry-owner-registry-v1/manifest.json','516ee3390c8ac829351f212f78b8659b0eaf712b457b37a487cfd5961fb18cef')
    require(not set(TEST_PATHS)&set(prior['suiteNames']),'no completed current suite replay')
    methods={};test_files=[]
    for binary,(path,count) in TEST_PATHS.items():
        file=data.ROOT/path;text=file.read_text();test_files.append(file)
        require(data.sha(file.read_bytes())==hashes[path],'whole original Test')
        names=re.findall(r'@Test\s+void\s+(\w+)\(',text)
        require(len(names)==len(set(names))==text.count('@Test')==count,'whole original methods')
        require(data.sha(file.read_bytes())=='60c3a7e9a4da798ca5c70d9dee0462e645d8f8721c6ffcddd0395af21baf11fa','fixed whole reviewed InspectorDeployment source')
        require(all(t in text for t in ['builder.environment().clear();','builder.environment().putAll(environment);','return execute(command, Map.of());','process.waitFor(20, TimeUnit.SECONDS)','if (process.isAlive()) process.destroy();','UnitSyntaxFixture.environment(directory)','void realMainBridge()','System.getProperty("java.class.path")']),'owned bounded process and fixed child argv graph')
        methods[binary]=names
    for p in EXTRAS:require(data.sha((data.ROOT/p).read_bytes())==hashes[p],'same original Unit syntax fixture')
    require(all(data.sha(Path(p).read_bytes())==h for p,h in TOOLS.items()),'fixed bounded tool binaries')
    guard_text={p:(snapshot/p).read_text() for p in CHILD_GUARD_FILES}
    require('String root = value(environment, ROOT, 4096);' in guard_text[CHILD_GUARD_FILES[1]] and 'if (value == null' in guard_text[CHILD_GUARD_FILES[1]],'empty environment rejects before factory')
    require('var configuration = InspectorLaunchConfiguration.read(arguments, environment);' in guard_text[CHILD_GUARD_FILES[0]] and 'factory.create(configuration.settings())' in guard_text[CHILD_GUARD_FILES[0]],'configuration precedes native factory')
    require('if (selected == null) return Optional.empty();' in guard_text[CHILD_GUARD_FILES[3]] and 'if (profile.isEmpty()) return Optional.empty();' in guard_text[CHILD_GUARD_FILES[4]],'no reserved child agent means no native exporter/private file')
    require(all('-javaagent:' not in (snapshot/p).read_text() for p in PUBLIC_FILES if p.endswith('.template')),'production wrapper child has no agent forwarding')
    runtime=data.read_checked(data.BASE/RUNTIME[0]/'manifest.json',RUNTIME[1])
    require(runtime['source']==SOURCE and runtime['actualExit']==0,'runtime library reference only')
    deps=runtime['begin']['dependencyHashes'];require(all(data.sha(Path(p).read_bytes())==h for p,h in deps.items()),'fixed dependencies')
    command=runtime['stages'][0]['command'];entries=command[command.index('-cp')+1].split(os.pathsep)
    require(entries[0].endswith('/pg17216-bootstrap-credential-values-twenty-pt-v1/fresh-test-classes') and all(p in deps for p in entries[1:]),'drop old Test classes')
    helper=data.ROOT/'tools/quality/architecture/InspectorDeploymentEightCurrentJunitLauncher.java'
    reporter=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    require(proof['actualExit']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(reporter.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','reporter identity')
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'fresh-test-classes';classes.mkdir()
    fixture=SLOT/'public-fixture-root';fixture.mkdir()
    for p in PUBLIC_FILES:
        destination=fixture/p;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/p,destination);require(data.sha(destination.read_bytes())==hashes[p],'owned exact public input copy')
    extra_files=[data.ROOT/p for p in EXTRAS]
    cp=os.pathsep.join([str(classes),*entries[1:]])
    agent=next(p for p in deps if p.endswith('org.jacoco.agent-0.8.15-runtime.jar'))
    inputs={p:hashes[p] for p in PUBLIC_FILES}
    begin=dict(source=SOURCE,invocation=invocation,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),normalManifestSha256=pin,sourceHashes=hashes,readOnlyPublicInputs=inputs,readOnlyFixtureRoot=str(fixture),normalSnapshotReadOnlyPath=str(snapshot),childBoundarySourceHashes={p:hashes[p] for p in CHILD_GUARD_FILES},toolBinaryHashes=TOOLS,ownJavaChildCount=1,childJavaAgentPresent=False,childJavaCoverageClaimed=False,childBusinessAdmissionProvenByFixedEmptyEnvironment=False,actualOwnFixtureWrites=True,actualUnitSyntaxOnly=True,dependencyHashes=deps,testSourceHashes={str(p):data.sha(p.read_bytes()) for p in [*test_files,*extra_files,helper,reporter]},selectedMethods=methods,selectedSuites={b:n for b,(_,n) in TEST_PATHS.items()},runtimeLibraryReference=list(RUNTIME),priorProductResultsTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    data.write(SLOT/'begin.safe.json',begin);runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin'
    stages=[runner.step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(p) for p in [*test_files,*extra_files,helper,reporter]]],SLOT,timeout=180)]
    if stages[0]['actualExit']==0 and not stages[0]['timedOut']:
        stages.append(runner.step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Dnk.pt.repository='+str(fixture),'-javaagent:'+agent+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION,'-cp',cp,helper.stem,str(SLOT/'xml')],SLOT,timeout=180))
    cases=[];xmls={};suites={}
    if len(stages)==2:
        for file in (SLOT/'xml').glob('TEST-*.xml'):
            xml=ET.parse(file).getroot();xmls[file.name]=data.sha(file.read_bytes());suites[xml.get('name')]={k:int(xml.get(k,'0')) for k in ['tests','failures','errors','skipped']}
            for c in xml.findall('testcase'):cases.append(dict(classname=c.get('classname'),name=c.get('name'),result='PASS' if not list(c) else 'NOT_PASS'))
    expected={(b,n) for b,names in methods.items() for n in names}
    passed=len(stages)==2 and all(s['actualExit']==0 and not s['timedOut'] for s in stages) and len(cases)==8 and {(c['classname'],c['name']) for c in cases}==expected and all(c['result']=='PASS' for c in cases) and set(suites)==set(TEST_PATHS) and all(suites[b]==dict(tests=n,failures=0,errors=0,skipped=0) for b,(_,n) in TEST_PATHS.items())
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items()),'all original inputs remain')
    require(all(data.sha(Path(p).read_bytes())==h for p,h in {**deps,**begin['testSourceHashes']}.items()),'tools and runtime unchanged')
    public_receipts={}
    evidence=fixture/'src/schubert-nk-api/target/inspector-deployment'
    for path in sorted(evidence.glob('*/*.json')) if evidence.exists() else []:
        blob=path.read_bytes();receipt=json.loads(blob)
        require(set(receipt)=={'method','command','exitCode','stdout','stderr'} and receipt['method'] in methods[next(iter(TEST_PATHS))] and path.parent.name==receipt['method'],'original method-owned public receipt')
        require(not any(v in str(receipt) for v in ['JAVA_TOOL_OPTIONS=','CREDENTIALS_DIRECTORY=','INVOCATION_ID=']),'no environment/credential diagnostic capture')
        public_receipts[str(path.relative_to(fixture))]=data.sha(blob)
    require(not passed or len(public_receipts)==50,'all fifty original tool receipts, not process totals')
    require(all(data.sha((fixture/p).read_bytes())==h for p,h in inputs.items()) and all(data.sha(Path(p).read_bytes())==h for p,h in TOOLS.items()),'public sources and fixed tools unchanged')
    environment={}
    if len(stages)==2:
        with (SLOT/'selected-junit.stdout').open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):
                    k,v=line.strip().split('=',1);require(k not in environment,'unique original env');environment[k]=v
        require(len(environment)==4,'original own JVM environment')
    verify(invocation)
    result=dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,tests=len(cases),suites=suites,cases=cases,xmlHashes=xmls,execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,sessionIdentity=SESSION,reportedEnvironment=environment,publicReceiptHashes=public_receipts,originalTopLevelToolReceipts=len(public_receipts),actualTotalProcessCount=None,ownFixtureWritesOnly=True,ownChildJavaBoundary='EMPTY_ENV_REJECTS_BEFORE_FACTORY_AND_NO_RESERVED_AGENT_NATIVE_EXPORT_DISABLED',childJavaCoverageClaimed=False,javaMainCredit=0,sourceChanged=False,newTestIds=0,newAccepted=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,productResultsTransferred=False,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result);OUT.mkdir();data.write(OUT/'manifest.json',result)
    for name in xmls:shutil.copyfile(SLOT/'xml'/name,OUT/name)
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=len(cases),suites=len(suites))));raise SystemExit(result['actualExit'])
if __name__=='__main__':main()
