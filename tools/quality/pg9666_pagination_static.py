"""Current six Main SpotBugs plus new Test source PMD/Checkstyle; no suite or application run."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
WORK = ROOT.parent / 'pgpt-runs/PG379'
TC = ROOT.parent / 'toolchain'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
NORMAL = WORK / 'pg9660-pagination-six-compile-v1/snapshot'
SLOT = WORK / 'pg9666-pagination-static-v1'
OUT = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9666-pagination-static-v1'
ENV = dict(PATH=str(TC / 'jdk-25.0.4/bin') + ':/usr/bin:/bin', LANG='C.UTF-8', JAVA_HOME=str(TC / 'jdk-25.0.4'),
    MAVEN_USER_HOME=str(TC / 'm2'), MAVEN_SKIP_RC='true', MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')


def step(label, command, cwd, timeout=180):
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    data.write(SLOT / (label + '-begin.safe.json'), dict(command=command, cwd=str(cwd), startUTC=start, environment=ENV))
    with (SLOT / (label + '.stdout')).open('xb') as stdout, (SLOT / (label + '.stderr')).open('xb') as stderr:
        child = subprocess.Popen(command, cwd=cwd, env=ENV, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, close_fds=True)
        data.write(SLOT / (label + '-process.safe.json'), dict(pid=child.pid, ownerPid=os.getpid(), command=command, cwd=str(cwd), startUTC=start))
        timed_out = False
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            child.kill()
            code = child.wait(timeout=15)
    value = dict(actualExit=code, timedOut=timed_out, startUTC=start, endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        command=command, cwd=str(cwd), stdoutSha256=data.sha((SLOT / (label + '.stdout')).read_bytes()),
        stderrSha256=data.sha((SLOT / (label + '.stderr')).read_bytes()))
    data.write(SLOT / (label + '-exit.safe.json'), value)
    return value


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    host = data.read_checked(ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9662-pagination-boundary-host-v1/manifest.json',
        'c5dfb7e4137c0c96833bcba4a3a3c6ec5cba04a54b3134d13b7395d808cbc19e')
    assert host['actualExit'] == 0 and host['source'] == SOURCE
    assert subprocess.check_output(['git', 'diff', '--name-only', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT) == b''
    for path, digest in normal['begin']['inputHashes'].items():
        assert data.sha((ROOT / path).read_bytes()) == data.sha((NORMAL / path).read_bytes()) == digest
    assert not list(NORMAL.glob('src/*/target/surefire-reports/TEST-*.xml'))
    os.umask(0o077)
    SLOT.mkdir()
    test = ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadPaginationBoundaryTest.java'
    file_list = SLOT / 'source-list.txt'
    with file_list.open('x') as stream:
        stream.write(str(test) + '\n')
    static = TC / 'static-gates-20261015'
    rules = ROOT / 'tools/quality/static'
    pmd = [static / 'record-fix-v1/pmd-record-1298.jar', *sorted((static / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tool_hashes = {str(p): data.sha(p.read_bytes()) for p in [*pmd, static / 'checkstyle-14.3.0-all.jar', rules / 'pmd.xml', rules / 'checkstyle.xml']}
    jdk = TC / 'jdk-25.0.4/bin'
    aux = os.pathsep.join(host['begin']['dependencyHashes'])
    stages = {}
    stages['pmd-test'] = step('pmd-test', [str(jdk / 'java'), '-cp', os.pathsep.join(map(str, pmd)),
        'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(file_list), '--rulesets', str(rules / 'pmd.xml'),
        '--use-version', 'java-25', '--minimum-priority', '5', '--aux-classpath', aux, '--no-cache', '--format', 'xml', '--report-file', str(SLOT / 'pmd.xml')], SLOT)
    stages['checkstyle-test'] = step('checkstyle-test', [str(jdk / 'java'), '-jar', str(static / 'checkstyle-14.3.0-all.jar'),
        '-c', str(rules / 'checkstyle.xml'), '-f', 'xml', '-o', str(SLOT / 'checkstyle.xml'), '@' + str(file_list)], SLOT)
    modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
    stages['spotbugs-six'] = step('spotbugs-six', [str(TC / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
        '-o', '--no-transfer-progress', '-Dmaven.repo.local=' + str(TC / 'm2/repository'),
        '-pl', ','.join('src/schubert-nk-' + m for m in modules), '-am', '-DskipTests=true',
        'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'], NORMAL, timeout=600)
    reports = {}
    for name, filename, tag in [('pmd-test', 'pmd.xml', 'violation'), ('checkstyle-test', 'checkstyle.xml', 'error')]:
        path = SLOT / filename
        root = ET.parse(path).getroot()
        nodes = [n for n in root.iter() if n.tag.rpartition('}')[2] == tag]
        errors = [n for n in root.iter() if n.tag.rpartition('}')[2] in ('error', 'configerror')] if name == 'pmd-test' else []
        reports[name] = dict(findings=len(nodes), processingErrors=len(errors), sha256=data.sha(path.read_bytes()),
            rawFindings=[dict(n.attrib, message=' '.join(''.join(n.itertext()).split())) for n in nodes])
    for module in modules:
        path = NORMAL / ('src/schubert-nk-' + module) / 'target/spotbugsXml.xml'
        root = ET.parse(path).getroot()
        reports['spotbugs-' + module] = dict(findings=len(root.findall('.//BugInstance')),
            processingErrors=len(root.findall('.//MissingClass')) + len(root.findall('.//Error')),
            sha256=data.sha(path.read_bytes()))
    passed = all(s['actualExit'] == 0 and not s['timedOut'] for s in stages.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    assert not list(NORMAL.glob('src/*/target/surefire-reports/TEST-*.xml'))
    assert all(data.sha(Path(p).read_bytes()) == h for p, h in tool_hashes.items())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p, h in normal['begin']['inputHashes'].items())
    assert all(data.sha(Path(item['path']).read_bytes()) == item['sha256'] for item in normal['jars'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0 if passed else 1, source=SOURCE, invocation=invocation,
        timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), stages=stages, reports=reports,
        testSourceSha256=data.sha(test.read_bytes()), toolHashes=tool_hashes, sourceInputsUnchanged=True,
        productTestsExecuted=0, checkstylePmdScope='NEW_TEST_SOURCE_ONLY', spotbugsScope='ALL_SIX_CURRENT_MAIN_MODULES',
        wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, suppressionsAdded=False))
    print(json.dumps(dict(actualExit=0 if passed else 1, reports={name: {k: value[k] for k in ('findings', 'processingErrors')} for name, value in reports.items()})))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
