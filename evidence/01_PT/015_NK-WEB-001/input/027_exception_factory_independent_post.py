"""Independently qualify the original four cases; no Test/Product invocation or old exec union."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile

R = Path(__file__).resolve().parents[4]
RUNS = R.parent/'pgpt-runs/PG379'
U = RUNS/'pg22220-exception-filter-factory-four-unit-v1'
REC = RUNS/'pg22224-exception-factory-metadata-recovery-v1'
OUT = R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22228-exception-factory-independent-post-v1'
SOURCE = 'aa101fb7c3c8b53d5218ca6dd3bd8db2973eb493'
CORE = '7aed8eace7c844c2f79f2e39db766faf914890d5'
P = 'dev/codex/schubert/nk/web/'
TARGET = P+'security/WebAccessExceptionFilterFactory'
DRIVER = 'evidence/01_PT/015_NK-WEB-001/input/024_exception_filter_factory_qualifier.py'
sha = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p:json.loads(Path(p).read_bytes())


def main():
    assert not OUT.exists()
    m = load(REC/'manifest.json')
    assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'],m['productTestsReexecuted']) == (0,4,0,0,0,0)
    assert m['originalCollectorWrapperExit'] == 1 and m['source'] == SOURCE and m['productionCoreMain'] == CORE
    b = load(U/'begin.json')
    assert b == m['begin'] and b['source'] == SOURCE and b['normalSource'] == CORE
    for name,h in m['originalFilesUnmodified'].items():
        assert sha(U/name) == h
    original_collector = R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22222-exception-factory-physical-collector-failure-v1/original-collector.py'
    for path,h in b['inputHashes'].items():
        assert hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=R)).hexdigest() == h
        assert sha(original_collector if path == DRIVER else R/path) == h
    assert sha(R/DRIVER) != b['inputHashes'][DRIVER]  # repair is a separately retained tool revision.
    terminal = load(U/'unit-exit.safe.json')
    assert terminal == m['originalUnitTerminal'] and terminal['actualExit'] == 0 and not terminal['timedOut']
    assert sha(U/'unit.stdout') == terminal['stdoutSha256'] and sha(U/'unit.stderr') == terminal['stderrSha256']
    cmd = terminal['command']
    assert '-Dspring.security.strategy=MODE_THREADLOCAL' in cmd
    assert '-Djunit.jupiter.extensions.autodetection.enabled=false' in cmd and '-Djunit.jupiter.execution.parallel.enabled=false' in cmd
    assert cmd.count('--select-class') == 1 and '--scan-classpath' not in cmd
    for path,h in b['dependencies'].items():
        assert sha(path) == h
        assert not any(x in path for x in ['/schubert-nk-api/','/schubert-nk-bootstrap/','/schubert-nk-batch/','/postgresql/','/artemis-','/playwright/'])
    normal_path = RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
    normal = load(normal_path)
    assert sha(normal_path) == b['normalManifestSha256'] == 'b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
    assert normal['actualExit'] == 0 and normal['source'] == CORE
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert sha(normal['jars']['web']['path']) == normal['jars']['web']['sha256']
        assert {n for n in jar.namelist() if n == TARGET+'.class' or n.startswith(TARGET+'$')} == {TARGET+'.class'}
        assert hashlib.sha256(jar.read(TARGET+'.class')).hexdigest() == m['physical'][TARGET] == sha(REC/'component'/(TARGET+'.class'))
    test_path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/WebAccessExceptionFactoryPortTest.java'
    expected = {'factoryRejectsMissingHandlerAndRetainsTheExactEntryPointInFreshFilters',
                'navigationAuthenticationFailureSavesExactlyOneRelativeStringAndRedirects',
                'nonnavigationAndAccessDeniedUseConfiguredHandlersWithoutCreatingAServletSession',
                'ordinaryAndNonsecurityFailureKeepOriginalObjectsAndNeverUseSessionOrAudit'}
    assert set(re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/test_path).read_text())) == expected
    cases = []
    environment = {}
    for path in sorted((U/'xml').glob('TEST-*.xml')):
        root = E.parse(path).getroot()
        for case in root.findall('testcase'):
            assert not case.findall('failure') and not case.findall('error') and not case.findall('skipped')
            assert case.get('classname') == 'dev.codex.schubert.nk.web.security.WebAccessExceptionFactoryPortTest'
            cases.append(case.get('name'))
        for prop in root.findall('./properties/property'):
            if prop.get('name') in ['java.version','os.name','os.arch','file.encoding','user.timezone']:
                environment[prop.get('name')] = prop.get('value')
    assert len(cases) == len(set(cases)) == 4 and set(cases) == {x+'()' for x in expected}
    assert len(m['cases']) == 4
    tree = E.parse(REC/'coverage.xml').getroot()
    counters = {x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')}
    assert counters == m['counters'] and all(v['missed'] == 0 for v in counters.values()) and 'BRANCH' not in counters
    assert counters['LINE']['covered'] == 5 and counters['METHOD']['covered'] == 2 and counters['CLASS']['covered'] == 1
    assert {n.get('name') for n in tree.findall('.//package/class')} == {TARGET}
    ex = (REC/'execinfo.stdout').read_text()
    ids = {name:crc for crc,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(REC/'classinfo.stdout').read_text())}
    assert set(ids) == {TARGET} and ex.count('Session "') == 1 and 'Session "PG22220-EXCEPTION-FACTORY4"' in ex
    probe = re.search(r'^'+ids[TARGET]+r'\s+(\d+) of\s+(\d+)\s+'+re.escape(TARGET)+r'$',ex,re.M)
    assert probe and probe[1] == probe[2]
    for stage in m['metadataStages'].values():
        assert stage['actualExit'] == 0 and not stage['timedOut']
    allowed = {
      'logging/WebSecurityAudit$Event': {'<init>','<clinit>'},
      'logging/WebSecurityAudit$Route': {'<init>','<clinit>'},
      'logging/WebSecurityAudit': {'<init>','record','version','canonicalAddress','lambda$record$1','<clinit>'},
      'session/SessionPayloadCodec': {'<init>','validateKey','close','<clinit>'},
      'session/JdbcWebSessionStore': {'<init>'},
      'session/SpringEncryptedSessionRepository': {'<init>'},
      'session/SessionAttributeCodec': {'<init>','<clinit>'},
      'session/EncryptedWebSessionRepository': {'<init>'},
      'session/EncryptedSessionPayload': {'validateVersion'},
      'security/ClosedWebAuthentication': {'principal'},
      'security/LoginClientAddress': {'<init>'},
      'security/EncryptedSessionRequestCache': {'<init>','saveRequest','requireConfigured','candidate'},
      'security/WebRequestContext': {'<init>','requestId','clientAddress','require','existing','<clinit>'},
      'security/WebAccessExceptionFilterFactory': {'<init>','create'},
      'security/SavedScreenTarget': {'<init>','fromGet','location','<clinit>'},
      'security/WebAccessFailureHandler': {'<init>','commence','isNavigation','handle','<clinit>'},
      'security/SavedRequestTarget': {'<init>','fromGet','location','require','<clinit>'},
    }
    actual = {}
    for node in E.parse(REC/'all-web-methods.xml').getroot().findall('.//package/class'):
        hit = [dict(name=x.get('name'),desc=x.get('desc')) for x in node.findall('method') if any(int(c.get('covered')) > 0 for c in x.findall('counter'))]
        if hit:
            actual[node.get('name')] = hit
    assert {name:{x['name'] for x in methods} for name,methods in actual.items()} == {P+name:methods for name,methods in allowed.items()}
    assert len(actual) == 17
    # The logged generated lambda owners are exactly the reviewed source bodies, not arbitrary Main.
    init = set(re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()))
    test_prefixes = [P+'security/WebAccessExceptionFactoryPortTest',P+'session/SecurityContextOwnerPortFixture']
    extras = {n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in actual and not any(n.startswith(v) for v in test_prefixes)}
    lambda_counts = {}
    for name in extras:
        owners = [P+'logging/WebSecurityAudit',P+'security/WebRequestContext']
        owner = next((x for x in owners if re.fullmatch(re.escape(x)+r'\$\$Lambda\+0x[0-9a-f]{16}',name)),None)
        assert owner is not None
        lambda_counts[owner] = lambda_counts.get(owner,0)+1
    assert lambda_counts == {P+'logging/WebSecurityAudit':3,P+'security/WebRequestContext':1}
    assert not any(n.startswith(('dev/codex/schubert/nk/api/','dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/storage/',P+'bootstrap/WebStartupException','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in init)
    assert not any(n in actual for n in [P+'session/SessionStoreException',P+'session/SpringWebSession'])
    static_path = R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22218-exception-filter-factory-four-static-v1/manifest.json'
    static = load(static_path)
    assert static['inputHashes'] == b['inputHashes'] and static['rawPmdExit'] == 4 and static['pmdRaw'] == 1
    assert static['applicableViolations'] == static['checkstyle'] == static['spotbugs'] == static['processingErrors'] == 0
    assert all(v['classification'] == 'NOT_APPLICABLE' and v['reason'] for v in static['individualClassifications'])
    assert sha(static['staticManifest']['path']) == static['staticManifest']['sha256']
    OUT.mkdir()
    files = {}
    for base,prefix in [(U,'original-'),(REC,'recovery-')]:
        for path in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
            if path.is_file() and path.name != "jacoco.exec":
                name = prefix+('class-init.stdout' if path.name == 'class-init.log' else path.name)
                assert name not in files
                shutil.copyfile(path,OUT/name)
                files[name] = sha(OUT/name)
    # The binary is the one original synthetic execution, named canonically for the publisher.
    shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec')
    files['jacoco.exec'] = sha(OUT/'jacoco.exec')
    (OUT/'executed-main-methods.json').write_text(json.dumps(actual,indent=2)+'\n')
    files['executed-main-methods.json'] = sha(OUT/'executed-main-methods.json')
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,
                  source=SOURCE,productionCoreMain=CORE,tests=4,newUniqueTests=4,
                  failures=0,errors=0,skipped=0,productTestsReexecuted=0,
                  originalCollectorExit=1,originalUnitExit=0,metadataRecoveryExit=0,
                  inputHashes=b['inputHashes'],physical=m['physical'],classIds=ids,counters=counters,
                  branchStatus='NATURAL_ZERO_BRANCH',branchRatio=None,sourceProofNew=1,
                  sourceMethods=sorted(expected),environment=environment,dependencies=b['dependencies'],
                  originalRun=dict(path=str(U/'begin.json'),sha256=sha(U/'begin.json')),
                  recoveryManifest=dict(path=str(REC/'manifest.json'),sha256=sha(REC/'manifest.json')),
                  staticClassification=dict(path=str(static_path.relative_to(R)),sha256=sha(static_path)),
                  executedMainClasses=17,hiddenLambdaOwnersAndCounts=lambda_counts,
                  heapMockSessionSavedGetOnly=True,ownHeapAuditCallback=True,realAuthentication=False,
                  realEncryptedSessionOrDbOrCryptoOrWire=False,heldFourInitialisations=0,
                  supportWholeSourceCredit=0,originalSourceTestsUnchanged=True,oldExecCombined=False,
                  manualExclusions=[],newAcceptance=0,formalUpdated=False,whole451Accepted=False,
                  effortRate=None,files=files,
                  verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__)),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,tests=4,newUniqueTests=4,newSourceProofs=1,manifestSha256=sha(OUT/'manifest.json'))))


if __name__ == '__main__':
    main()
