"""Three complete original Root memory-fixture suites; no native provider or external resources."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/platform/'
NAME=PREFIX+'InspectorStaticEnvironment'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='164f6dfe9f1143f86b868ada1b0a7d5a5687b6fc42fc901941a4f0193f702258')}
CLOSURES={NAME:[NAME]}
METADATA=set()
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'InspectorStaticEnvironmentTest':6}
PINS={'InspectorStaticEnvironmentTest':'c5b577e45049173c254f6e79a24c8645275674e6d1f64489e6ae0ebc867bc855'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG17006-INSPECTOR-STATIC-ENVIRONMENT-ORIGINAL6'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PUBLIC_TEMPLATE='src/deployment/config/inbox-inspector.env.template'
PUBLIC_TEMPLATE_SHA='2f8514321264c8fa67d73694ce7a441a7e3450ab520a60f0c052364304ab3f73'
PLAN=data.BASE/'PG17005-inspector-static-environment-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
def public_repository_step(name,command):
    if name=='selected-junit':
        assert not any(v.startswith('-Dnk.pt.repository=') for v in command)
        command=[command[0],'-Dnk.pt.repository='+str(ROOT),*command[1:]]
    return environmental_step(name,command)
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16996-current2525-morning-service-readiness-registry-v1/manifest.json','a8b22c3233bb63a34f4c945ddfbfb6cddddaee16f3c1f17d2ef3a354482b97fa')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    assert current[PUBLIC_TEMPLATE]==data.sha((ROOT/PUBLIC_TEMPLATE).read_bytes())==PUBLIC_TEMPLATE_SHA
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,testPublicSourceRead=True,reviewedPublicSourceReads={PUBLIC_TEMPLATE:PUBLIC_TEMPLATE_SHA},reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17006-inspector-static-environment-six-pt-v1';run.OUT=data.BASE/'PG17006-inspector-static-environment-six-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/InspectorStaticEnvironmentSixCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['InspectorStaticEnvironmentTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=public_repository_step;run.main()
