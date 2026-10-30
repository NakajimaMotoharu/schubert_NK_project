"""Original API inputs4; supplied source/Map/Path values only, no private IO/native startup."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'ApiStartupInputsTest':4}
SESSION='PG15340-ORIGINAL-API-INPUTS4'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'ApiStartupInputsTest':'3cecaf9d04173e9b973683a95f94a566ac47506654cad33170134814a54be3d5'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15340-api-startup-inputs-four-pt-v1';run.OUT=data.BASE/'PG15340-api-startup-inputs-four-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalApiStartupInputsJunitLauncher.java';run.NEW_TEST=TESTS['ApiStartupInputsTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15331-current1760-exact11-owner-registry-v3/manifest.json','cfb7c63e1b0761397371bf5fef625b7014aff588b992c35619c99b633374bd9f')
    assert not {'dev.codex.schubert.nk.api.bootstrap.'+name for name in COUNTS}&set(registry['suiteNames'])
    target='dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs'
    main='src/schubert-nk-api/src/main/java/'+target+'.java'
    assert main not in {n+'.java' for n in registry['fullSourceUnits']}
    assert normal['begin']['inputHashes'][main]==run.host.sha(data.ROOT/main)=='e6d69bfa6580bba22f2558c37d0ab43799ee5cc515e00a8d64370168333648e6'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        assert {p[:-6] for p in jar.namelist() if p==target+'.class' or p.startswith(target+'$') and p.endswith('.class')}=={target,target+'$Values'}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert len(re.findall(r'@Test\b',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','getConnection(','DataSource','PreparedStatement','.production('])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert not re.search(r'(?<![A-Za-z0-9_])Files\s*\.',text)
        assert '"dev.codex.schubert.nk.api.bootstrap.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
        assert 'new ApiProcessMain(' not in text and '.run(' not in text and '.main(' not in text
    run.step=environmental_step;run.main()
