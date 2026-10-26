"""Bind the new SQL-interface oracle to normal bytes, raw static diagnostics and one PT run."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '9eac6bffd8462aea5d0d0759cb14fdef5b1a1a3e'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionSqlContractTest.java'
OUT = data.BASE/'PG10084-question-sql-quality-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10076-question-sql-six-compile-v1/manifest.json',
        '9ba6f1fabcda3a665fd2222fd21a9c2c6095ae773ec1cb37b408374ae8bc287d')
    previous = data.read_checked(data.BASE/'PG10062-log-sql-six-compile-v1/manifest.json',
        '2dcf40f6e754c945996de612411200237048d64afcae6080e376be644308bfe0')
    static = data.read_checked(data.BASE/'PG10074-question-sql-precommit-static-v1/manifest.json',
        '29b6e3792a79debde2f1abcd224350d3e1292abedda4e927d1225d6badfe9f1f')
    pt_hash = 'c3c001763eb2794795447ea287333eea752b0fa1162d967a26ec9e54137eb907'
    pt = data.read_checked(data.BASE/'PG10082-question-sql-post-v1/manifest.json',pt_hash)
    assert normal['source'] == pt['source'] == SOURCE
    assert normal['actualExit'] == previous['actualExit'] == pt['actualExit'] == 0
    assert normal['testsExecuted'] == 0 and static['source'] is None and static['baseSource'] == previous['source']
    hashes = normal['begin']['inputHashes']
    assert set(hashes)-set(previous['begin']['inputHashes']) == {TEST}
    assert all(hashes[p] == h for p,h in previous['begin']['inputHashes'].items())
    assert static['sourceHashes'] == {TEST:hashes[TEST]}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 2
    assert static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    details = static['reports']['pmd']['details']
    assert {(r['rule'],r['beginline']) for r in details} == {('UseProperClassLoader','366'),('UseConcurrentHashMap','374')}
    source = (data.ROOT/TEST).read_text()
    assert 'QuestionSqlContractTest.class.getClassLoader()' in source
    assert 'private final Map<Integer, @Nullable Object> parameters = new HashMap<>()' in source
    assert not any(x in source for x in ('new Thread(', 'ExecutorService', 'parallelStream(', '@SuppressWarnings', 'NOPMD'))
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test, new_test = test_classes(previous), test_classes(normal)
    assert len(old_test) == 1928 and len(new_test) == 1931 and all(new_test[p] == h for p,h in old_test.items())
    added = set(new_test)-set(old_test)
    prefix = 'dev/codex/schubert/nk/api/application/question/QuestionSqlContractTest'
    assert added == {('api',prefix+n+'.class') for n in ('','$Call','$Jdbc')}
    java = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(java) == 1803 and sum('/src/main/java/' in p for p in java) == 965
    assert pt['tests'] == 16 and pt['newTestIds'] == 8 and pt['suites'] == 2
    assert pt['forbiddenProductProbeHits'] == 0 and not pt['coverageUnion']
    assert pt['questionRequestFour100'] and not pt['targetUnitsFour100']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        currentJavaPaths=1803,currentMainPaths=965,currentTestPaths=838,
        mainClassesUnchanged=1843,previousTestClassesUnchanged=1928,testClasses=1931,addedTestClasses=sorted(added),
        precommitStaticSourceWasNull=True,staticSourceHashesExactlyMatchCommittedCompilation=True,
        rawStaticExit=1,rawPmdFindings=2,checkstyleFindings=0,suppressionsAdded=False,
        individualApplicability=[dict(rule='UseProperClassLoader',line=366,status='NON_APPLICABLE_CONTEXT',
            reason='standalone host public JDK-interface proxy; not a JavaEE managed component'),
            dict(rule='UseConcurrentHashMap',line=374,status='NON_APPLICABLE_CONTEXT',
            reason='one fixture per sequential test, confined callback map; no thread/executor/parallel stream')],
        currentSourceTests=16,newTestIds=8,relatedRegressionMethods=8,suites=2,units=pt['units'],
        currentPtManifestSha256=pt_hash,forbiddenProductProbeHits=0,
        remaining='Repository exceptional/invalid-row branches and actual PostgreSQL contracts unexecuted; F03/451/native/CHR and QA051 held',
        productTestsReexecuted=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainClassesUnchanged=1843,newMethods=8,javaPaths=1803,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
