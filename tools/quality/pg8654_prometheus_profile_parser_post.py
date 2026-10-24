"""Original actual parser8 independent source/XML/log/exec-session proof, no new coverage scope."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import scoped_prometheus_post as post
import pg8652_prometheus_profile_parser_host as original
from host_tool_invocation import capture, verify

host = post.host
RUN = host.W / 'pg8652-prometheus-profile-parser-host-v1'
SLOT = host.W / 'pg8654-prometheus-profile-parser-post-v1'
OUT = host.BASE / 'PG8654-prometheus-profile-parser-post-v1'
RAW_SHA = 'e093e13bd04eff95006fb2df115cfe5472a6366b494c29fb29d5841c522db7b3'

def destinations(run, slot, out):
    return (run == host.W / 'pg8652-prometheus-profile-parser-host-v1'
            and slot == host.W / 'pg8654-prometheus-profile-parser-post-v1'
            and out == host.BASE / 'PG8654-prometheus-profile-parser-post-v1')

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert destinations(RUN,SLOT,OUT)
    destination_negatives = []
    for name,args in (('foreign-run',(host.W/'pg8644-metric-payload-precision-host-v1',SLOT,OUT)),('foreign-slot',(RUN,host.W/'pg8646-metric-payload-precision-post-v1',OUT)),('foreign-out',(RUN,SLOT,host.BASE/'PG8646-metric-payload-precision-post-v1'))):
        assert not destinations(*args)
        destination_negatives.append(name)
    assert not SLOT.exists() and not OUT.exists()
    assert host.sha(RUN / 'manifest.safe.json') == RAW_SHA
    raw = json.loads((RUN / 'manifest.safe.json').read_text())
    post.common.SOURCE = original.SOURCE
    post.COUNTS = original.COUNTS
    post.assess(raw)
    assert host.sha(original.COMPILE / 'manifest.safe.json') == original.COMPILE_SHA
    normal = json.loads((original.COMPILE / 'manifest.safe.json').read_text())
    assert normal['source'] == original.SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == 0 and normal['testsExecuted'] == 0
    assert subprocess.check_output(['git', 'diff', '--name-only', original.SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT) == b''
    for path, digest in normal['begin']['inputHashes'].items():
        assert host.sha(host.ROOT / path) == host.sha(original.COMPILE / 'snapshot' / path) == digest
    for key in ('dependencyHashes', 'testSourceHashes', 'emptyConfigHashes', 'fixtureHashes'):
        assert all(host.sha(Path(p)) == h for p,h in raw['begin'][key].items())
    assert host.sha(RUN / 'jacoco.exec') == raw['execSha256']
    actual = []
    for path in sorted((RUN / 'xml').glob('TEST-*.xml')):
        assert host.sha(path) == raw['xmlHashes'][path.name]
        suite = ET.parse(path).getroot()
        assert raw['suites'][suite.get('name')] == {k:int(suite.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        for case in suite.findall('testcase'):
            assert not list(case)
            actual.append((case.get('classname'), case.get('name')))
    expected = {('dev.codex.schubert.nk.web.monitoring.PrometheusProfileParserTest', method) for method in ('promparse001ActualDebugAccepted','promparse002ActualStandardAccepted','promparse003MalformedRejected','promparse004UnknownFieldRejected','promparse005InvalidDurationRejected','promparse006DuplicateJobRejected','promparse007TimeoutExceedsIntervalRejected','promparse008WrongScrapeTypeRejected')}
    assert len(actual) == len(set(actual)) == 8 and set(actual) == expected == {(r['classname'],r['name']) for r in raw['cases']}
    for stage, name in zip(raw['stages'], ('fresh-test-compile.log','selected-junit.log')):
        assert stage['actualExit'] == 0 and not stage['timedOut'] and host.sha(RUN / name) == stage['logSha256']
    log = (RUN / 'selected-junit.log').read_text()
    import hashlib
    rows = [line.split('\t') for line in log.splitlines() if line.startswith('PROMPARSE\t')]
    negative_inputs = ['{', '{"unknown_nk_field": true}', '{"global":{"scrape_interval":"NOT_DURATION"}}', '{"scrape_configs":[{"job_name":"duplicate"},{"job_name":"duplicate"}]}', '{"global":{"scrape_interval":"1s","scrape_timeout":"2s"}}', '{"scrape_configs":"not_a_list"}']
    negative_hashes = {hashlib.sha256(value.encode()).hexdigest() for value in negative_inputs}
    positive_hashes = set(original.PROFILES.values())
    assert len(rows)==8 and len({row[1] for row in rows})==8
    assert {row[1] for row in rows} == positive_hashes | negative_hashes
    for row in rows:
        assert len(row)==4 and len(row[3])==64
        assert int(row[2])==0 if row[1] in positive_hashes else int(row[2]) in (1,3)
    assert host.sha(original.TOOL)==original.TOOL_SHA
    profile_pins = {str(host.ROOT / ('src/deployment/monitoring/prometheus/'+name+'.yml.template')):digest for name,digest in original.PROFILES.items()}
    assert all(host.sha(Path(path))==digest for path,digest in profile_pins.items())
    environment = {}
    for key in ('runtime.version','os.name','os.arch','os.version'):
        values = [line.split('=',1)[1] for line in log.splitlines() if line.startswith(key + '=')]
        assert len(values) == 1 and values[0]
        environment[key] = values[0]
    assert environment['runtime.version'].startswith('25.0.4+') and environment['os.name'] == 'Linux'
    assert raw['begin']['environment'] == post.common.ENV
    assert '-javaagent:' + str(post.common.AGENT) + '=destfile=' + str(RUN / 'jacoco.exec') + ',append=false,sessionid=PG8652-PROMETHEUS-PROFILE-PARSER' in raw['stages'][1]['command']
    rejected = []
    for name, mutate in (
        ('source-tail', lambda r:r.update(source=post.different_source_tail(r['source']))),
        ('failed-case', lambda r:r['cases'][0].update(result='NOT_PASS')),
        ('duplicate-case', lambda r:r['cases'].__setitem__(1,copy.deepcopy(r['cases'][0]))),
        ('fixture-change', lambda r:r['begin'].update(fixtureHashes={'unknown':'0'*64})),
        ('coverage-union', lambda r:r['begin'].update(priorCoverageTransferred=True)),
        ('formal-inflation', lambda r:r.update(formalUpdated=True)),
        ('timeout-pass', lambda r:r['stages'][1].update(timedOut=True))):
        candidate = copy.deepcopy(raw)
        mutate(candidate)
        try:
            post.assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('every metadata guard rejects')
    core = host.TC / 'm2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    qualified = host.BASE / 'PG8636-api-web-custom-payload-post-v1/manifest.json'
    assert host.sha(qualified) == 'e2062ef8e44f0ec3a4e758179c78c24bbe946afde4d738129363643ea9c5b1a9'
    # Core is the same metadata reader library used by the last real qualified post.
    prior = json.loads(qualified.read_text())
    assert host.sha(core) == prior['readerLibraryHashes'][str(core)]
    SLOT.mkdir()
    classes = SLOT / 'reader'
    classes.mkdir()
    post.SLOT = SLOT
    helper = host.ROOT / 'tools/quality/architecture/MetricCoexistenceSessionAudit.java'
    jdk = host.TC / 'jdk-25.0.4/bin'
    compiled, _ = post.step('session-reader-compile', [str(jdk / 'javac'), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', str(core), '-d', str(classes), str(helper)])
    assert compiled['actualExit'] == 0
    checked, output = post.step('original-session-metadata', [str(jdk / 'java'), '-cp', str(classes) + os.pathsep + str(core), 'MetricCoexistenceSessionAudit', str(RUN / 'jacoco.exec'), 'PG8652-PROMETHEUS-PROFILE-PARSER'])
    assert checked['actualExit'] == 0
    session = [line.split('\t') for line in output.splitlines() if line.startswith('SESSION\t')]
    assert len(session) == 1 and len(session[0]) == 5 and session[0][1] == 'PG8652-PROMETHEUS-PROFILE-PARSER' and int(session[0][4]) > 0
    foreign, foreign_output = post.step('foreign-session-rejected', [str(jdk / 'java'), '-cp', str(classes) + os.pathsep + str(core), 'MetricCoexistenceSessionAudit', str(RUN / 'jacoco.exec'), 'PG8652-FOREIGN'])
    assert foreign['actualExit'] == 1 and 'SESSION\t' not in foreign_output
    assert host.sha(RUN / 'jacoco.exec') == raw['execSha256']
    verify(invocation)
    OUT.mkdir()
    safe_log = [line for line in log.splitlines() if line.startswith(('runtime.version=','os.name=','os.arch=','os.version=','found=','PROMPARSE\t'))]
    value = dict(actualExit=0, source=original.SOURCE, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), invocation=invocation, originalManifestSha256=RAW_SHA, normalManifestSha256=original.COMPILE_SHA, normalCompileReplayed=False, tests=8, suites=1, failed=0, errors=0, skipped=0, cases=raw['cases'], xmlHashes=raw['xmlHashes'], execSha256=raw['execSha256'], actualEnvironment=environment, redactedJvmOutput=safe_log, originalLogOmittedLines=len(log.splitlines())-len(safe_log), actualSessions=1, parserInvocations=rows, parserBinarySha256=original.TOOL_SHA, profileHashes=profile_pins, parserCommand=['check','config','--lint=all','--lint-fatal','owned-public-file'],  sessionMetadata=session[0], sessionReader=dict(sourceSha256=host.sha(helper),coreSha256=host.sha(core),compileReceipt=compiled,receipt=checked,foreignRejected=foreign,targetInitialized=False), newNegativeGuards=rejected, productionSourceChanged=False, newProductionClasses=0, coverageQualified=False, staticQualificationAdded=False, coverageUnion=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, fixedOfflineProductParserVerified=True, providerOrEndpointAccepted=False, productTestsExecutedByPost=0, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, tests=8, suites=1, session='PG8652-PROMETHEUS-PROFILE-PARSER', coverageQualified=False, manifestSha256=host.sha(OUT / 'manifest.json'))))
