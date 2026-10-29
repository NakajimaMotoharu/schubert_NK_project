"""Original whole UserCreate value-form8; no account creation/auth or external resource operation."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'UserCreateFormTest':8}
SESSION='PG14288-ORIGINAL-WEB-USER-CREATE8'
ROOT=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'UserCreateFormTest':'3366b1d112fc8b0f729bd7fbdad445a84c2f8743886879bccfa3a14d7e4dbc20'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

_original_step=run.step
def environmental_step(name,command):
    result=_original_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        log=run.SLOT/'selected-junit.log'
        assert run.host.sha(log)==result['logSha256']
        values={};size=0
        with log.open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if not line:break
                size+=len(line.encode());assert size<=4096
                for key in ('runtime.version','os.name','os.arch','os.version'):
                    if line.startswith(key+'='):
                        value=line[len(key)+1:].rstrip('\\n')
                        assert key not in values and re.fullmatch('[A-Za-z0-9._+ -]{1,128}',value)
                        values[key]=value
        assert len(values)==4 and values['runtime.version'].startswith('25.0.4') and values['os.name']=='Linux'
        result['reportedEnvironment']=values
        result['environmentBasis']='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14288-web-user-create-whole-eight-pt-v1'
    run.OUT=run.host.BASE/'PG14288-web-user-create-whole-eight-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalWebUserCreateJunitLauncher.java'
    run.NEW_TEST=TESTS['UserCreateFormTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
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
