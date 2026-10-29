"""Original Target8 and Mutation16 pure value/DTO suites; no actual business or authority operation."""
import re
from pg14282_current_pt_environment_post import headers
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'TargetOperationFormTest':8,'UserMutationFormTest':16}
SESSION='PG14296-ORIGINAL-WEB-TARGET-MUTATION24'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'TargetOperationFormTest':'2e0ddf8c3369a6a2a17a264cac49e55b18f472e86eb11aad6a3ec50423eeb00c','UserMutationFormTest':'c9d1ce61914955f60048577ed9a2221afb18663f5d8beadc51056e84be819412'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

_original_step=run.step
def environmental_step(name,command):
    result=_original_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        log=run.SLOT/'selected-junit.log'
        assert run.host.sha(log)==result['logSha256']
        lines=[]
        with log.open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if not line:break
                lines.append(line)
        assert sum(len(x.encode()) for x in lines)<=4096
        result['reportedEnvironment']=headers(lines)
        result['environmentBasis']='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14296-web-target-mutation-whole-twenty-four-pt-v1'
    run.OUT=run.host.BASE/'PG14296-web-target-mutation-whole-twenty-four-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalWebTargetMutationJunitLauncher.java'
    run.NEW_TEST=TESTS['TargetOperationFormTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.web.form.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
