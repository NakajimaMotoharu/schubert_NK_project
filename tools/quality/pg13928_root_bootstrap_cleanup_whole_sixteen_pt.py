"""Original whole16 memory boundary callbacks; no actual Root, ADMIN or Cleanup execution."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'RootServiceAdmissionScopeTest':6,'BootstrapEntryBoundaryTest':5,'CleanupPreflightTest':5}
SESSION = 'PG13928-ROOT-BOOTSTRAP-CLEANUP-MEMORY-CURRENT-WHOLE16'
ROOT = run.host.ROOT
TESTS = {name:ROOT/('src/schubert-nk-'+('api' if name.startswith('Bootstrap') else 'batch')+'/src/test/java/dev/codex/schubert/nk/'+('api/bootstrap' if name.startswith('Bootstrap') else 'batch/file')+'/'+name+'.java') for name in COUNTS}
PINS = {'RootServiceAdmissionScopeTest':'71560f91ff65ee491900b4ef86083f429afee1524d4f5f05ff8cba6df9a8bd71',
    'BootstrapEntryBoundaryTest':'0f56a6cce8881002a8210daf81a6c19328badd632fa3b63d597d683ec5de3fc8',
    'CleanupPreflightTest':'b5577eb35b6a8db2b53b5b2faf03b80dd4b63feaa542cee3d147837d13fde12a'}
EXTRAS = {
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java':'62a55866ed181dd886a8b5988fa5922675259b261ad31133a601c7b8361dcbf4',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java':'dc52d8ad7f4cc73b2947257e458bb8e36f10221789218812c44010c72951e976'}
REPORTER = ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13928-root-bootstrap-cleanup-whole-sixteen-pt-v1'
    run.OUT = run.host.BASE/'PG13928-root-bootstrap-cleanup-whole-sixteen-pt-v1'
    run.HELPER = ROOT/'tools/quality/architecture/RootBootstrapCleanupMemoryJunitLauncher.java'
    run.NEW_TEST = TESTS['RootServiceAdmissionScopeTest']
    run.TEST_SOURCE_OVERRIDES = {n:p for n,p in TESTS.items() if n != run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES = (REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert all(run.host.sha(ROOT/p) == sha for p,sha in EXTRAS.items())
    for name,path in TESTS.items():
        text = path.read_text();assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','new BackupArtifactFixture','new BootstrapAdminMain(','RootStartupContext.create(','StartupAdmissionFile.create('])
        assert '"dev.codex.schubert.nk.'+('api.bootstrap.' if name.startswith('Bootstrap') else 'batch.file.')+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
