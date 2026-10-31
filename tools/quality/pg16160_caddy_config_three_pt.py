"""Unchanged original three-case parser/template suite in a new exclusive public fixture root."""
import re
import subprocess
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='f0d5b21a34e7e9d5879663ee49e4645d34115aef60b2d3119594cf9c424a731f')}
CLOSURES={NAME:[NAME]}
METADATA=set()
UNEXECUTED=set()
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
TEST=ROOT/'CaddyPublicConfigurationTest.java'
TEST_SHA='a7cde1d1a189e6e835084e612d83e87b0d51925a8a17374f97005301019daa9c'
TESTS={'CaddyPublicConfigurationTest':TEST}
COUNTS={'CaddyPublicConfigurationTest':3}
FIXTURES={}
SESSION='PG16160-ORIGINAL-CADDY-CONFIG-THREE'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURE_ROOT=run.host.W/'pg16160-caddy-config-three-pt-v1'
TEMPLATE='src/deployment/caddy/Caddyfile.template'
TEMPLATE_SHA='2914bfd4134186911562071f92652ce750e513213a749672dd161615c3d8763c'

def source_path(row):
    return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

def original_step(name,command):
    destination=FIXTURE_ROOT/'deployment/caddy/Caddyfile.template'
    assert run.host.sha(destination)==TEMPLATE_SHA
    result=environmental_step(name,command)
    assert run.host.sha(destination)==TEMPLATE_SHA
    assert [str(p.relative_to(FIXTURE_ROOT/'deployment')) for p in (FIXTURE_ROOT/'deployment').rglob('*') if p.is_file()]==['caddy/Caddyfile.template']
    return result

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=FIXTURE_ROOT/'test-cwd';run.OUT=data.BASE/'PG16160-caddy-config-three-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalCaddyConfigThreeJunitLauncher.java'
    run.NEW_TEST,run.TEST_ROOT=TEST,ROOT
    run.TEST_SOURCE_OVERRIDES,run.FIXTURES,run.COUNTS={},FIXTURES,COUNTS
    run.EXTRA_TEST_SOURCES,run.SESSION_ID=(REPORTER,),SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    text=TEST.read_text();assert run.host.sha(TEST)==TEST_SHA and text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==3
    assert text.count('Files.readString(')==1 and 'Path.of("../deployment/caddy/Caddyfile.template")' in text
    assert not any(v in text for v in ['@Before','ProcessBuilder','HttpClient','DriverManager','RootStartupContext','KeyStore','FingerprintKeyRing','ResponseSnapshotCodec'])
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG16088-current2133-canonical-aad-registry-v1/manifest.json','b6e7dc918a723fd30965322bc8400e51a786872204ea72a99f3e9b18534e30b7')
    assert normal['source']==current['source']==SOURCE and 'dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest' not in current['suiteNames']
    test_relative=str(TEST.relative_to(data.ROOT))
    assert normal['begin']['inputHashes'][test_relative]==run.host.sha(COMPILE/'snapshot'/test_relative)==TEST_SHA
    for row in MAIN_UNITS.values():
        path=source_path(row)
        assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:
            assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME}
    fixture=(data.ROOT/TEMPLATE).read_bytes()
    assert data.sha(fixture)==TEMPLATE_SHA and subprocess.check_output(['git','show',SOURCE+':'+TEMPLATE],cwd=data.ROOT)==fixture
    assert not FIXTURE_ROOT.exists() and not run.OUT.exists()
    FIXTURE_ROOT.mkdir(mode=0o700)
    destination=FIXTURE_ROOT/'deployment/caddy/Caddyfile.template';destination.parent.mkdir(parents=True)
    with destination.open('xb') as stream:stream.write(fixture)
    data.write(FIXTURE_ROOT/'template-binding.safe.json',dict(source=SOURCE,originalPath=TEMPLATE,originalSha256=TEMPLATE_SHA,
        copiedPath=str(destination),copiedSha256=run.host.sha(destination),testCwd=str(run.SLOT),
        sourceGitShowMatched=True,publicTemplateOnly=True,externalDeploymentChanged=False))
    run.step=original_step;run.main()
