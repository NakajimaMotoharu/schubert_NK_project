"""Current-source whole8; reuse unchanged static review only, never old Product results."""
import json
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture\":{\"module\":\"api\",\"name\":\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture\",\"sha256\":\"eb55a81e4acb996cd04dccf7bc1ba16787bb2893e035cd2ad958a3e47b0df8a2\"},\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture\":{\"module\":\"web\",\"name\":\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture\",\"sha256\":\"7c6ec6a2be8cabf0b13efb9a1c8ce012a009a1c3bc6a0847851fe899d84e3326\"},\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop\":{\"module\":\"web\",\"name\":\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop\",\"sha256\":\"0cedc1417ddc419a11896516ad7e2d76cd6277c42711815120f35191e1cd7a6a\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture\":[\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Capture\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Factory\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Open\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Operation\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Owner\"],\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture\":[\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Capture\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Factory\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Open\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Operation\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Owner\"],\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop\":[\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop\",\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop$Step\"]}")
METADATA=set(json.loads("[\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Capture\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Factory\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Open\",\"dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Operation\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Capture\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Factory\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Open\",\"dev/codex/schubert/nk/web/bootstrap/WebTerminalCapture$Operation\",\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop$Step\"]"))
COUNTS=json.loads("{\"ApiTerminalCaptureTest\":3,\"WebTerminalCaptureTest\":3,\"WebRuntimeStopTest\":5}")
PINS=json.loads("{\"ApiTerminalCaptureTest\":\"b3d30d3a406c41637613154913d115085f9007f1157189e876417ea831232686\",\"WebTerminalCaptureTest\":\"d5c8c512c291b011e4cc82b699d0782423bc27da57f79fa9150283ed76fe1dc4\",\"WebRuntimeStopTest\":\"d38668723e67f81c94c184dde8a960f44aa9056b75814df3fc8d90653a75f55c\"}")
EXTRAS=json.loads("{}")
FIXTURES=json.loads("{}")
SESSION='PG16680-API-WEB-TERMINAL-STOP-ORIGINAL-ELEVEN'
ROOT=data.ROOT
TESTS={name:data.ROOT/path for name,path in json.loads("{\"ApiTerminalCaptureTest\":\"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiTerminalCaptureTest.java\",\"WebTerminalCaptureTest\":\"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebTerminalCaptureTest.java\",\"WebRuntimeStopTest\":\"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStopTest.java\"}").items()}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16679-terminal-stop-static-review-equivalence-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG13920-api-web-terminal-stop-whole-eleven-pt-v1/manifest.json','7b14223c627f48aecc36d1378772b84afdacfffadfef1a736a2c1b50c7fda739')
    before=old['begin']['sourceHashes'];current=normal['begin']['inputHashes']
    changed=sorted(p for p in before.keys()|current.keys() if before.get(p)!=current.get(p))
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
    assert changed==sorted(prefix+p for p in ['question/QuestionQueryApplicationService.java','admin/UserQueryApplicationService.java','log/LogQueryApplicationService.java'])
    assert normal['source']==SOURCE and old['source']=='0061d178cda80c2ce3926290619c64db125dbcfc'
    previous=data.read_checked(data.BASE/'PG16670-current2339-root-scope-registry-v1/manifest.json','09aca6c61c9049691cb7bfa7f5c35741a814a9e1ab4c87591de6cd6e9d00caac')
    assert previous['source']==SOURCE and not set(MAIN_UNITS)&previous['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));text=path.read_text()
        assert run.host.sha(path)==PINS[name]==current[relative]==before[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert ('.'.join(path.relative_to(data.ROOT).as_posix().split('/src/test/java/',1)[1][:-5].split('/'))) not in previous['suiteNames']
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningParentBudget.create','MorningProcessMain.runCompleted(','MorningProcessMain.main(','RootFailedStartRecovery'])
    for path,pin in EXTRAS.items():assert run.host.sha(ROOT/path)==pin==current[str((ROOT/path).relative_to(data.ROOT))]==before[str((ROOT/path).relative_to(data.ROOT))]
    for path,pin in FIXTURES.items():assert run.host.sha(data.ROOT/path)==pin==current[path]==before[path]
    for name,row in MAIN_UNITS.items():
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            path=source_path(row);assert row['sha256']==current[path]==before[path]==run.host.sha(data.ROOT/path)
            assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    reviews=['evidence/01_PT/018_NK-OPS-001/2538_APIWeb終端停止memory全11_通常PT仕様.md']
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reuseKind='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS',priorSource=old['source'],priorPublicInputManifestSha256='7b14223c627f48aecc36d1378772b84afdacfffadfef1a736a2c1b50c7fda739',currentNormalManifestSha256=COMPILE_SHA,changedPathsOutsideReviewedBatchCallTree=changed,reviewDocuments={p:run.host.sha(data.ROOT/p) for p in reviews},originalWholeSuites=COUNTS,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16680-api-web-terminal-stop-original-eleven-pt-v1';run.OUT=data.BASE/'PG16680-api-web-terminal-stop-original-eleven-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/ApiWebTerminalStopMemoryJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiTerminalCaptureTest'];run.TEST_ROOT=TESTS['ApiTerminalCaptureTest'].parent
    run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    assert str(run.AGENT).startswith(str(run.host.TC)+'/m2/') and not str(run.AGENT).startswith('/opt/pgpt-tools-pg390/')
    assert not {'JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS'} & set(run.ENV)
    def checked_current_argv_step(name,command):
        if name=='selected-junit':
            agents=[v for v in command if v.startswith('-javaagent:')]
            assert len(agents)==1 and agents[0].startswith('-javaagent:'+str(run.AGENT)+'=') and not agents[0].startswith('-javaagent:/opt/pgpt-tools-pg390/')
            assert not any(v.startswith(('-agentlib:','-agentpath:')) for v in command)
        return environmental_step(name,command)
    run.step=checked_current_argv_step;run.main()
