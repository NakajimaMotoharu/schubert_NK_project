"""Original API/Web non-secret config14; only fixed strings and three public normal-snapshot templates."""
import re
import subprocess
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"ApiNonSecretConfigTest":7,"WebNonSecretConfigTest":7}
PACKAGES={"ApiNonSecretConfigTest":"dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest","WebNonSecretConfigTest":"dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest"}
TESTS={n:data.ROOT/p for n,p in {"ApiNonSecretConfigTest":"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java","WebNonSecretConfigTest":"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfigTest.java"}.items()}
PINS={"ApiNonSecretConfigTest":"c48aaae03b6901d3511ac2cda416c0f184044b6baefcf307d64c69997937a63c","WebNonSecretConfigTest":"d56e00afaac0bfe0dd269d689b10df907a0f04a31e6021837a180ccea7f0b78b"}
TEMPLATES={"src/deployment/config/common.yml.template":"d61acf911e08a15cfdb2700eb81db7bbbb920cb3ccd80f1665652af4b4b7880a","src/deployment/config/api.yml.template":"206f4ed29da0fca31c1bab15015eb5b4db93255846c411f5d1815050d66bf267","src/deployment/config/web.yml.template":"3e9a7ba4ada50e82e450cdd634439c2c122fed051de089010dee07dfd2d25cb7"}
FIXTURES={}
SESSION='PG15222-ORIGINAL-NONSECRET-CONFIG14'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def config_step(name,command):
    if name=='selected-junit':
        assert not any(value.startswith('-Dnk.pt.repository=') for value in command)
        command=[command[0],'-Dnk.pt.repository='+str(COMPILE/'snapshot'),*command[1:]]
    return environmental_step(name,command)

def templates(normal):
    for relative,pin in TEMPLATES.items():
        original=subprocess.check_output(['git','show',SOURCE+':'+relative],cwd=data.ROOT)
        assert data.sha(original)==normal['begin']['inputHashes'][relative]==pin
        for path in [data.ROOT/relative,COMPILE/'snapshot'/relative]:
            assert path.is_file() and not path.is_symlink() and data.sha(path.read_bytes())==pin

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15222-nonsecret-config-fourteen-pt-v1';run.OUT=data.BASE/'PG15222-nonsecret-config-fourteen-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalNonSecretConfigJunitLauncher.java';run.NEW_TEST=TESTS['ApiNonSecretConfigTest'];run.TEST_ROOT=data.ROOT/'src/schubert-nk-bootstrap/src/test/java'
    run.TEST_SOURCE_OVERRIDES={'WebNonSecretConfigTest':TESTS['WebNonSecretConfigTest']};run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15212-current1697-borrowed-outbox-registry-v1/manifest.json','1aa2ef15483fc5f64130c25ac6de40de80ed860d1debd4659aac82b722f816cc')
    assert not set(PACKAGES.values())&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==data.sha(path.read_bytes())==data.sha((COMPILE/'snapshot'/relative).read_bytes())==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','getConnection(','HttpClient','HttpServer','System.getenv','setPosixFilePermissions','preserveFatal(','attachSecondary(','Class.forName('])
        assert '"'+PACKAGES[name]+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    templates(normal);run.step=config_step
    try:run.main()
    finally:templates(normal)
