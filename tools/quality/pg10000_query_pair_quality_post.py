"""Bind two new pure Tests to prior static bytes and unchanged complete normal production code."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = 'bba24d15923831a17e5464328b70fdb950fb2fcf'
OUT = data.BASE/'PG10000-query-pair-quality-post-v1'
NEW = {
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionQueryPlainContractTest.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogPlainContractTest.java'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    previous = data.read_checked(data.BASE/'PG9968-plain-core-fixed-six-compile-v1/manifest.json',
        '277ca65ee5a596e94d9e222d919ed8acd4e3a7efe72883446b769db41e51363f')
    static = data.read_checked(data.BASE/'PG9991-query-pair-precommit-static-v2/manifest.json',
        'f32ceb56c585247af6fed792be0dc3f05398bfbe0b6560669ac0216e46244a4f')
    pt = data.read_checked(data.BASE/'PG9998-query-pair-post-v1/manifest.json',
        '9cc448696e53581d68239ac67cb22ae25a019c2a41d04ebaf2ec9b0f15bfa9d8')
    assert normal['source'] == pt['source'] == SOURCE
    assert normal['actualExit'] == previous['actualExit'] == static['actualExit'] == pt['actualExit'] == 0
    assert normal['testsExecuted'] == 0 and static['source'] is None and static['baseSource'] == previous['source']
    hashes = normal['begin']['inputHashes']
    assert set(hashes)-set(previous['begin']['inputHashes']) == NEW
    assert all(hashes[p] == h for p,h in previous['begin']['inputHashes'].items())
    assert set(static['sourceHashes']) == NEW
    assert all(hashes[p] == h for p,h in static['sourceHashes'].items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test, new_test = test_classes(previous), test_classes(normal)
    assert len(old_test) == 1920 and len(new_test) == 1922 and all(new_test[p] == h for p,h in old_test.items())
    added = set(new_test)-set(old_test)
    assert added == {('api','dev/codex/schubert/nk/api/application/question/QuestionQueryPlainContractTest.class'),
        ('api','dev/codex/schubert/nk/api/application/log/LogPlainContractTest.class')}
    java = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(java) == 1800 and sum('/src/main/java/' in p for p in java) == 965
    assert pt['tests'] == pt['newTestIds'] == 16 and pt['suites'] == 2 and not pt['coverageUnion'] and not pt['targetUnitsFour100']
    assert not any('assertThrows(RuntimeException.class' in (data.ROOT/p).read_text() for p in NEW)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        currentJavaPaths=1800,currentMainPaths=965,currentTestPaths=835,
        mainClassesUnchanged=1843,previousTestClassesUnchanged=1920,testClasses=1922,addedTestClasses=sorted(added),
        precommitStaticSourceWasNull=True,staticSourceHashesExactlyMatchCommittedCompilation=True,
        rawPmdFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        currentSourceTests=16,newTestIds=16,suites=2,units=pt['units'],
        currentPtManifestSha256='9cc448696e53581d68239ac67cb22ae25a019c2a41d04ebaf2ec9b0f15bfa9d8',
        remaining='normal repository query dispatch/nonnull guards remain unexecuted; database/native/CHR/F03/451 and QA051 held',
        productTestsReexecuted=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainClassesUnchanged=1843,newMethods=16,javaPaths=1800,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
