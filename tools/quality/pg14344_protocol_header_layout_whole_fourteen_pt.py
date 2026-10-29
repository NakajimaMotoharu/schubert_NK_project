"""Three original header/layout suites14 and two independent public TSV fixtures; pure values only."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'HeaderModelTest':7,'LayoutMetadataTest':4,'LayoutFieldCatalogTest':3}
SESSION='PG14344-ORIGINAL-PROTOCOL-HEADER-LAYOUT14'
ROOT=run.host.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/header'
TESTS={name:(ROOT if name=='HeaderModelTest' else ROOT.parent/'layout')/(name+'.java') for name in COUNTS}
PINS={'HeaderModelTest':'2f20adba3d3b4dfa8eef16e36ad571f91c7ffffa9b080a15a04f1bfddabd631f','LayoutMetadataTest':'e3ea04e5b8a49be88eb3e0adcd2f5b5bc5a20f6793ba9e3be632545fe282b436','LayoutFieldCatalogTest':'ad2df79ad437b878561567c4364f458336669c1c0394c0c5e602b529bae483ef'}
FIXTURES={'src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b','src/schubert-nk-protocol/src/test/resources/protocol/layouts-ui233.tsv':'c4f290595f5cabf19c11877e2dea95627b4d42490116431bac3bfde58950d711'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14344-protocol-header-layout-whole-fourteen-pt-v1'
    run.OUT=run.host.BASE/'PG14344-protocol-header-layout-whole-fourteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalProtocolHeaderLayoutJunitLauncher.java'
    run.NEW_TEST=TESTS['HeaderModelTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='HeaderModelTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.protocol.'+('header.' if name=='HeaderModelTest' else 'layout.')+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
