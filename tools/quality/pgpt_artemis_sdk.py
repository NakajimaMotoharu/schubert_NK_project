"""Exact official client SDK for source-reviewed, nonconnecting whole MQ tests.

This opt-in never permits a broker, transport, native library or Product cache.
Legacy profiles continue to reject every Artemis JAR without this witness.
"""
from pathlib import Path
import hashlib
import json
import re

R = Path(__file__).resolve().parents[2]
TC = R.parent / 'toolchain/m2/repository'
WITNESS = ('evidence/01_PT/018_NK-OPS-001/evidence/'
           'PG28512-artemis-sdk-pure-whole-source-provenance-v1/manifest.json')
SDK_PATHS = frozenset([
    'org/apache/artemis/artemis-core-client/2.56.0/artemis-core-client-2.56.0.jar',
    'org/apache/artemis/artemis-commons/2.56.0/artemis-commons-2.56.0.jar',
    *[f'io/netty/netty-{n}/4.1.137.Final/netty-{n}-4.1.137.Final.jar'
      for n in ['common', 'buffer', 'transport']],
    'org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar',
])
MAIN_BASE = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/mq/'
MAIN_NAMES = frozenset([
    'ArtemisAcceptorReadinessClient', 'ArtemisAddressSettingsReadinessClient',
    'ArtemisManagementReadinessClient', 'ArtemisManagementReadinessException',
    'ArtemisQueuePressureClient', 'ArtemisReadinessClient', 'ArtemisReadinessException',
    'ArtemisRoleReadinessClient', 'ArtemisStartupObservation',
])
STORAGE = ('src/schubert-nk-storage/src/main/java/'
           'dev/codex/schubert/nk/storage/StorageIoException.java')
MAIN_PATHS = frozenset(MAIN_BASE + n + '.java' for n in MAIN_NAMES) | {STORAGE}
TEST_BASE = MAIN_BASE.replace('/src/main/', '/src/test/')
TEST_NAMES = frozenset([
    'ArtemisStartupObservationTest', 'ArtemisDetailedValuesTest',
    'ArtemisParentDeadlineTest', 'ArtemisManagementEncoderBoundaryTest',
    'AcceptorPolicyPortTest', 'AcceptorObjectBoundaryTest',
    'ArtemisCatalogFatalBoundaryTest',
])
TEST_PATHS = frozenset(TEST_BASE + n + '.java' for n in TEST_NAMES)
FORBIDDEN_INIT = frozenset([
    'org/apache/activemq/artemis/api/core/client/ActiveMQClient',
    'org/apache/activemq/artemis/api/core/client/ClientRequestor',
    'org/apache/activemq/artemis/core/client/impl/ServerLocatorImpl',
    'org/apache/activemq/artemis/core/server/embedded/EmbeddedActiveMQ',
    'org/apache/activemq/artemis/core/remoting/impl/netty/NettyConnector',
    'io/netty/channel/nio/NioEventLoopGroup',
    'io/netty/channel/epoll/EpollEventLoopGroup',
    'io/netty/channel/kqueue/KQueueEventLoopGroup',
])


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syntax(c):
    option = c.get('reviewedArtemisSdk')
    if option is None:
        return
    require(isinstance(option, dict) and set(option) == {'witness'}, 'SDK exact opt-in')
    pin = option['witness']
    require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and
            pin['path'] == WITNESS and isinstance(pin['sha256'], str) and
            re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'SDK exact provenance pin')
    require(pin in c.get('closureProofs', []), 'SDK witness explicit closure')
    jars = c.get('sdkJars', [])
    require(len(jars) == len(SDK_PATHS) and set(jars) == SDK_PATHS,
            'SDK exact six official client-only dependencies')
    require(set(c.get('mainSources', [])) == MAIN_PATHS and
            len(c['mainSources']) == len(MAIN_PATHS), 'SDK exact reviewed ten Main sources')
    tests = [x['path'] for x in c.get('testSources', [])]
    require(tests and len(tests) == len(set(tests)) and set(tests) <= TEST_PATHS,
            'SDK only reviewed whole pure tests; no embedded or extracted tests')
    require(c.get('reviewedGuardSignature') is not None, 'SDK real bounded Guard required')


def validate_witness(c, witness, source_hashes):
    """Pure metadata validation, before any dependency data access."""
    syntax(c)
    require(witness.get('actualExit') == 0 and witness.get('originalTests') == 26 and
            witness.get('wholeTestLinesReviewed') == 1090 and
            witness.get('artifactDataInspectionOnly') is True and
            witness.get('productClassesLoadedOrInitialized') is False and
            witness.get('productTestsExecuted') == 0 and
            witness.get('realBrokerRootNativeDbCredentialOperations') == 0 and
            witness.get('productCachedClassesOrApplicationJarReads') == 0 and
            witness.get('holdsUnchanged') is True, 'SDK data-only independent provenance')
    require(witness.get('mainInputHashes') == source_hashes and
            set(source_hashes) == MAIN_PATHS, 'SDK unchanged whole reviewed Main')
    rows = witness.get('sdkJars', [])
    require(len(rows) == len(SDK_PATHS) and {x['path'] for x in rows} == SDK_PATHS,
            'SDK complete unique provenance rows')
    for row in rows:
        path = row['path']
        require(row.get('savedCentralSha1Matched') is True and
                row.get('savedCentralPomSha1Matched') is True and
                row.get('productClassesOrNativeLibraries') == 0 and
                row.get('origin') == 'https://repo.maven.apache.org/maven2/' + path and
                row.get('purpose') == 'COMPILE_AND_PURE_PROXY_JSON_API_ONLY_NO_BROKER_NETWORK_NATIVE',
                'SDK origin and nonnative nonproduct purpose')
        require(c.get('preparedDependencyHashes', {}).get(str(TC / path)) == row['sha256'],
                'SDK exact frozen dependency hash')


def validate_test_text(text):
    require(not re.search(r'\b(?:EmbeddedActiveMQ|ServerLocatorImpl|RootStartupContext|'
                          r'FixedServiceIdentity|LinuxDirectoryCalls|LinuxInodeSecurity)\b|'
                          r'\bActiveMQClient\s*\.|\bnew\s+ClientRequestor\b|'
                          r'\.createSessionFactory\s*\(|\.createConsumer\s*\(|'
                          r'\bProcessBuilder\b|\bDriverManager\b|\bDataSource\b|'
                          r'\bClass\.forName\b|java\.lang\.foreign|java\.net\.Socket|'
                          r'@(?:BeforeAll|TestFactory|ParameterizedTest)\b', text),
            'SDK test must remain whole, pure and nonconnecting')
    require(not re.search(r'\.join\(\s*\)', text), 'SDK worker wait must be finite')


def checked(c):
    if c.get('reviewedArtemisSdk') is None:
        return None
    syntax(c)
    pin = c['reviewedArtemisSdk']['witness']
    require(digest(R / pin['path']) == pin['sha256'], 'SDK witness unchanged')
    witness = json.loads((R / pin['path']).read_text())
    hashes = {p: digest(R / p) for p in c['mainSources']}
    validate_witness(c, witness, hashes)
    for test in c['testSources']:
        validate_test_text((R / test['path']).read_text())
    for row in witness['sdkJars']:
        path = TC / row['path']
        require(path.is_file() and not path.is_symlink() and digest(path) == row['sha256'],
                'SDK actual official bytes, no replacement or fallback')
    return pin


def check_runtime(c, initialized):
    if c.get('reviewedArtemisSdk') is None:
        return None
    require(not FORBIDDEN_INIT.intersection(initialized),
            'SDK backend factory, requestor or event-loop initialized')
    return dict(witness=c['reviewedArtemisSdk']['witness'],
                forbiddenBackendInitializationsObserved=[],
                actualConnectionOrNativeAuthority=False)
