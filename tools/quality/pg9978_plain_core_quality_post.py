"""Bind current eight-PT result, static source and complete normal Main byte identity."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes

ROOT = data.ROOT
SOURCE = '70165b0768a1fabd13371cc25a55978fcf3452ba'
OUT = data.BASE/'PG9978-plain-core-quality-post-v1'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryCanonicalCoreTest.java'


def test_classes(normal):
    result = {}
    for module, item in normal['jars'].items():
        root = Path(item['path']).parent/'test-classes'
        for file in root.rglob('*.class'):
            result[(module, file.relative_to(root).as_posix())] = data.sha(file.read_bytes())
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG9968-plain-core-fixed-six-compile-v1/manifest.json',
        '277ca65ee5a596e94d9e222d919ed8acd4e3a7efe72883446b769db41e51363f')
    previous = data.read_checked(data.BASE/'PG9944-log-style-six-compile-v1/manifest.json',
        '9bd924d4baa1720b896451c96eee53c42f885afa213b8bca618ea4c4f9cd262d')
    pt = data.read_checked(data.BASE/'PG9974-plain-core-fixed-post-v1/manifest.json',
        '7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b')
    static = data.read_checked(data.BASE/'PG9976-plain-core-fixed-static-v1/manifest.json',
        'f47eec5e91e68323593fc2cfce79cbacda71323a4738d441b01b1006042d04b9')
    assert normal['source'] == pt['source'] == static['source'] == SOURCE
    assert normal['actualExit'] == pt['actualExit'] == previous['actualExit'] == 0
    assert normal['testsExecuted'] == 0 and pt['tests'] == 8 and pt['suites'] == 2
    hashes = normal['begin']['inputHashes']
    assert set(hashes)-set(previous['begin']['inputHashes']) == {TEST}
    assert all(hashes[p] == h for p,h in previous['begin']['inputHashes'].items())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(hashes[p] == h for p,h in static['sourceHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    old_main, new_main = jar_classes(previous), jar_classes(normal)
    assert old_main == new_main and len(new_main) == 1843
    old_test, new_test = test_classes(previous), test_classes(normal)
    added = set(new_test)-set(old_test)
    assert added == {('api','dev/codex/schubert/nk/api/application/admin/UserQueryCanonicalCoreTest.class')}
    assert all(new_test[p] == h for p,h in old_test.items()) and len(new_test) == 1920
    assert static['actualExit'] == 1
    assert static['reports']['pmd']['findings'] == 1 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    finding, = static['reports']['pmd']['details']
    text = (ROOT/TEST).read_text()
    assert finding['rule'] == 'CloseResource' and finding['variable'] == 'value'
    assert text.splitlines()[int(finding['beginline'])-1].strip() == 'var value = canonical.fields().get(index);'
    assert 'try (var canonical = request.canonical(actor);' in text
    canonical = ROOT/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/CanonicalRequest.java'
    assert 'fields.forEach(CanonicalField::close);' in canonical.read_text()
    applicability = dict(path=TEST,sourceSha256=hashes[TEST],rule='CloseResource',line=int(finding['beginline']),
        disposition='NOT_APPLICABLE_TO_EXACT_BORROWED_FIELD',
        reason='Enclosing try-with CanonicalRequest owns and closes its fields; borrowed getter is not independently owned. No suppression and no after-close/key-lifetime validation.')
    paths = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(paths) == 1798 and sum('/src/main/java/' in p for p in paths) == 965
    assert pt['counters'] == {'LINE':{'covered':54,'missed':8},'METHOD':{'covered':12,'missed':1},
        'CLASS':{'covered':1,'missed':0},'BRANCH':{'covered':16,'missed':2}}
    assert not pt['targetUnitFour100'] and not pt['coverageUnion']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    value = dict(actualExit=0,source=SOURCE,invocation=invocation,mainClassesUnchanged=1843,
        previousTestClassesUnchanged=len(old_test),testClasses=len(new_test),addedTestClasses=sorted(added),
        currentJavaPaths=1798,currentMainPaths=965,currentTestPaths=833,
        currentSourceTests=8,suites=2,newTestIds=4,relatedRegressionMethods=4,
        currentPtManifestSha256='7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b',
        counters=pt['counters'],rawPmdFindings=1,pmdApplicableFindings=0,checkstyleFindings=0,rawStaticExit=1,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        normalAndStaticSourceHashesMatch=True,suppressionsAdded=False,oldExecUnion=False,
        remaining='query normal repository dispatch and other non-null argument guards not executed; whole 451/F03/native/CHR/QA051 remain held',
        newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,mainClassesUnchanged=1843,tests=8,newIds=4,javaPaths=1798,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
