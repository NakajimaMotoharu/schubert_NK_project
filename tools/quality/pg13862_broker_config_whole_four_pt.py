"""Four whole public XML literal contracts; parser only, never an embedded broker."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'ArtemisBrokerConfigurationTest':4}
SESSION = 'PG13862-BROKER-PUBLIC-CONFIG-CURRENT-WHOLE4'
TESTS = {'ArtemisBrokerConfigurationTest':run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ArtemisBrokerConfigurationTest.java'}
REPORTER = run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
CONFIG = 'src/deployment/artemis/etc/broker.xml'
CONFIG_SHA = '161cbc5fc57ae38e4d75f45e8c752a781732aa3bf6c93c6d7ce8eb1cdaae1820'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13862-broker-config-whole-four-pt-v1'
    run.OUT = run.host.BASE/'PG13862-broker-config-whole-four-pt-v1'
    run.HELPER = run.host.ROOT/'tools/quality/architecture/BrokerPublicConfigurationCurrentJunitLauncher.java'
    run.NEW_TEST = TESTS['ArtemisBrokerConfigurationTest']
    run.TEST_SOURCE_OVERRIDES = {};run.EXTRA_TEST_SOURCES = (REPORTER,);run.FIXTURES = {}
    run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.NEW_TEST) == '8f3158a7b9ffe84312e4ac902e3d850ae9963b270302818fc737f1e6c1dfe1d9'
    text = run.NEW_TEST.read_text()
    assert text.count('@Test') == 4 and text.count('@BeforeAll') == 1
    assert len(re.findall(r'void (?:globalBrokerAndJournalSettingsMatchTheIndependentOracle|topologyAndTransportAreClosedToTheApprovedSet|addressPoliciesMatchTheIndependentCapacityMatrix|securityRolesMatchTheIndependentAclMatrix)\(\)',text)) == 4
    assert 'new FileConfigurationParser().parseMainConfig(input)' in text
    assert not any(term in text for term in ['EmbeddedActiveMQ','ActiveMQServers','DriverManager','ProcessBuilder','RootStartupContext','TemporaryInfrastructureException','WebStartupException','NativeReader'])
    config = COMPILE/'snapshot'/CONFIG
    assert run.host.sha(config) == CONFIG_SHA == run.host.sha(run.host.ROOT/CONFIG)
    xml = config.read_text()
    assert not any(term in xml for term in ['<!DOCTYPE','<!ENTITY','${','<xi:include','<broker-connections'])
    assert str(config) in run.HELPER.read_text()
    try:run.main()
    finally:assert run.host.sha(config) == CONFIG_SHA
