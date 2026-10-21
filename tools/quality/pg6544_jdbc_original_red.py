"""Read one existing original transaction red; no replay, no not-run promotion."""
import json
import os
import xml.etree.ElementTree as ET
from pg6544_jdbc_transaction_selected import W, BASE, TEST, guard_source, sha

RUN = W/'pg6544-jdbc-transaction-red-v1'
CLASS = 'dev.codex.schubert.nk.api.dispatch.JdbcTransactionFatal329Test'
METHODS = {
 'tx329001SqlPrimaryAndCloseFatalRetainIdentityAfterRollback',
 'tx329002ProtocolPrimaryAndCloseFatalCannotBecomeTemporary',
 'tx329003DirectFatalRollsBackOnceDespiteSecondaryAndSameClose',
 'tx329004CommitFatalWinsOverRollbackAndCloseFatals',
 'tx329007SqlNextCauseFatalCannotBecomeTheFixedCatalog'}


def validate_failure(method, node):
    if not node.get('type', '').endswith('AssertionFailedError'):
        raise ValueError('assertion, not compile/timeout/test error')
    message = node.get('message', '')
    if method == 'tx329004CommitFatalWinsOverRollbackAndCloseFatals':
        expected = ('expected: <[acquire, auto:false, handle, commit, rollback, close]> '
                    'but was: <[acquire, auto:false, handle, commit, close]>')
    else:
        expected = ('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
                    'but was: <dev.codex.schubert.nk.api.error.TemporaryInfrastructureException>')
    if message != expected:
        raise ValueError('exact independently predicted missing fatal/rollback assertion')


def inspect():
    path = RUN/'manifest.safe.json'; m = json.loads(path.read_bytes())
    begin = json.loads((RUN/'begin.safe.json').read_bytes()); guard_source(m['source'], 'red')
    if not (m['source'] == begin['source'] and m['actualExit'] == m['mavenActualExit'] == 1
            and m['phaseExits'] == [0, 0, 1] and m['sourceFixed'] and not m['selectedQualified']
            and (m['tests'], m['suites']) == (14, 5) and sha(RUN/'source.tar') == begin['archiveSha256']):
        raise ValueError('exact original genuine terminal and snapshot')
    count = 0; failures = set(); xmls = {}
    for path in (RUN/'source').glob('src/*/target/surefire-reports/TEST-*.xml'):
        root = ET.parse(path).getroot(); xmls[root.get('name')] = sha(path)
        for case in root.findall('testcase'):
            count += 1
            if any(n.tag in ('error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
                raise ValueError('no unexpected error/skip/flaky red')
            failure = case.find('failure')
            if failure is not None:
                method = case.get('name', '').split('(', 1)[0]
                if root.get('name') != CLASS or method not in METHODS:
                    raise ValueError('only preregistered five counterexamples')
                validate_failure(method, failure); failures.add(method)
    if count != 14 or len(xmls) != 5 or failures != METHODS:
        raise ValueError('all actual XML, no arithmetic PASS')
    return dict(actualExit=0, originalExit=1, source=m['source'], run=RUN.name,
        originalManifestSha256=sha(RUN/'manifest.safe.json'), archiveSha256=begin['archiveSha256'],
        testSha256=sha(RUN/'source'/TEST), tests=14, suites=5, expectedFailures=sorted(failures),
        xmlHashes=xmls, laterNotRun=6, testsExecutedByReader=0, formalAccepted=False,
        ptAlternativeCompleted=0, vmActions=0, bug='BUG-1592', rollout='YKT-1345')


def main():
    value = inspect(); out = BASE/'PG6544-jdbc-original-red-v1'; os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, redFailures=5, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
