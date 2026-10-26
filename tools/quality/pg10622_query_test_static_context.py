"""Thirty-nine exact source-context judgments; no Product class or Test execution."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '95894757e2bd7f392262497ea620873430ccc5f1'
OUT = data.BASE/'PG10622-query-test-static-context-v1'
WHY = {
    'NullAssignment': 'Test fault injector nullable reference is reset to disabled state; both fixture readers explicitly guard null before wrap. Not a missing production value or global nullability qualification.',
    'AvoidCatchingGenericException': 'Test afterCommit callback calls session(... ) throws Exception; catch immediately throws AssertionError(failure), does not swallow or normalize failure. Not production fallback handling.',
    'CloseResource': 'failing is only a Proxy alias of receiver; receiver is allocated and owned by enclosing try-with-resources. Proxy adds no JMS provider resource; do not independently close the borrowed receiver mid-Test.',
    'UseProperClassLoader': 'Standalone JUnit fixture uses exact JMSContext interface defining loader to implement that interface; not J2EE webapp/container or ambient context-loader discovery.',
    'DoNotUseThreads': 'JUnit-owned concurrency/interrupt stimulus, not production J2EE thread creation. Six executor scopes use try-with-resources and timed Future.get; interrupt cases restore test-thread interrupt in finally. Actual shutdown liveness and original DB/key Test execution remain unproven/HOLD.',
    'AvoidLiteralsInIfCondition': 'Five fixed commit ordinal condition literals need named Test-local first/second/third constants; BUG1853/YKT1604. Do not alter phase values or claim this source correction already implemented.',
}
FIXTURES = [
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserApplicationFixture.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogApplicationFixture.java',
]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10612-log-cleanup-literal-compile-v1/manifest.json',
        '7e484e3e66d5f8b678c933a8628d40e4ecb7d145d1f426d8372c9e22d411fcf1')
    static_path = data.BASE/'PG10610-log-cleanup-literal-static-v1/manifest.json'
    static = data.read_checked(static_path,'ece9dc5461f5cd2dd24a1a62c7a4bd3c9d236d8bec737fed23791401f4ceb8b5')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 39
    texts = {}
    for path,digest in static['sourceHashes'].items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == digest == normal['begin']['inputHashes'][path]
        texts[Path(path).stem] = (path,text)
    companion = {}
    for path in FIXTURES:
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        assert 'sqlFault == null ? actual : sqlFault.wrap(actual)' in text
        assert 'void session(long user, int contextNumber) throws Exception' in text
        companion[path] = data.sha(text.encode())
    counts = Counter()
    for _,text in texts.values():
        counts['ownedExecutorScopes'] += len(re.findall(r'\bvar pool = (?:java\.util\.concurrent\.)?Executors\.',text))
        counts['timedFutureWaits'] += len(re.findall(r'\b(?:future|result)\.get\((?:5|20|30),',text))
    assert counts == dict(ownedExecutorScopes=6,timedFutureWaits=6)
    cleanup = texts['CleanupStepRepositoryTest'][1]
    assert cleanup.count('Thread.interrupted();') == 2 and cleanup.count('Thread.currentThread().interrupt();') == 2
    rows = []
    for i,finding in enumerate(static['reports']['pmd']['details'],1):
        path,text = texts[finding['class']]
        start,end = int(finding['beginline']),int(finding['endline'])
        span = '\n'.join(text.splitlines()[start-1:end])
        rule = finding['rule']
        assert rule in WHY and span
        if rule == 'AvoidLiteralsInIfCondition':
            assert re.search(r'if \(f\.commits\.get\(\) == [123]\)',span)
        rows.append(dict(metadataId=f'STATIC-10622-{i:03d}',originalFinding=finding,
            path=path,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(span.encode()),
            disposition='ACTIONABLE_OPEN_BUG1853' if rule == 'AvoidLiteralsInIfCondition' else 'NOT_APPLICABLE_TO_EXACT_TEST_CONTEXT',
            reason=WHY[rule],dynamicQualification=False))
    assert Counter(r['originalFinding']['rule'] for r in rows) == {
        'DoNotUseThreads':18,'NullAssignment':10,'AvoidLiteralsInIfCondition':5,
        'AvoidCatchingGenericException':2,'CloseResource':2,'UseProperClassLoader':2}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'judgments.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        staticManifestSha256=data.sha(static_path.read_bytes()),judgmentsSha256=data.sha((OUT/'judgments.json').read_bytes()),
        sourceHashes=static['sourceHashes'],companionSourceHashes=companion,sourceContextCounts=dict(counts),
        reviewed=39,contextNotApplicable=34,actionable=5,pendingClassification=0,
        additionalDiscovery='BUG1852_SYSTEM_ERROR_RESULT_0200_NAME_MISMATCH',
        rawStaticExit=1,suppressionsAdded=False,actualExecutorShutdownLivenessProven=False,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,
        externalActions=0,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
