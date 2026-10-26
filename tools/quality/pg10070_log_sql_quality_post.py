"""Bind the new SQL-interface oracle to normal bytes, raw static diagnostics and one PT run."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '6cd6ae7efc495f17e1ebb79291f26c7a90f99dc7'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogSqlContractTest.java'
OUT = data.BASE/'PG10070-log-sql-quality-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10062-log-sql-six-compile-v1/manifest.json',
        '2dcf40f6e754c945996de612411200237048d64afcae6080e376be644308bfe0')
    previous = data.read_checked(data.BASE/'PG10040-user-sql-six-compile-v1/manifest.json',
        '37f90bd83ad135df52b631b603eb0b2859a9b21d86984615ea0829d46c3a2cf5')
    static = data.read_checked(data.BASE/'PG10060-log-sql-precommit-static-v1/manifest.json',
        '62b36da8038b8702f2d05e5d0a28e059e2b58107499d7a9cecf03eb1254d53ef')
    pt_hash = 'f909af4a8703b53aeef2903f23968393a88cfbff0efb713e231d90338f7ba8b2'
    pt = data.read_checked(data.BASE/'PG10068-log-sql-post-v1/manifest.json',pt_hash)
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
    assert {(r['rule'],r['beginline']) for r in details} == {('UseProperClassLoader','343'),('UseConcurrentHashMap','351')}
    source = (data.ROOT/TEST).read_text()
    assert 'LogSqlContractTest.class.getClassLoader()' in source
    assert 'private final Map<Integer, Object> parameters = new HashMap<>()' in source
    assert not any(x in source for x in ('new Thread(', 'ExecutorService', 'parallelStream(', '@SuppressWarnings', 'NOPMD'))
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test, new_test = test_classes(previous), test_classes(normal)
    assert len(old_test) == 1925 and len(new_test) == 1928 and all(new_test[p] == h for p,h in old_test.items())
    added = set(new_test)-set(old_test)
    prefix = 'dev/codex/schubert/nk/api/application/log/LogSqlContractTest'
    assert added == {('api',prefix+n+'.class') for n in ('','$Call','$Jdbc')}
    java = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(java) == 1802 and sum('/src/main/java/' in p for p in java) == 965
    assert pt['tests'] == 16 and pt['newTestIds'] == 8 and pt['suites'] == 2
    assert pt['forbiddenProductProbeHits'] == 0 and not pt['coverageUnion']
    assert pt['logRequestFour100'] and not pt['targetUnitsFour100']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        currentJavaPaths=1802,currentMainPaths=965,currentTestPaths=837,
        mainClassesUnchanged=1843,previousTestClassesUnchanged=1925,testClasses=1928,addedTestClasses=sorted(added),
        precommitStaticSourceWasNull=True,staticSourceHashesExactlyMatchCommittedCompilation=True,
        rawStaticExit=1,rawPmdFindings=2,checkstyleFindings=0,suppressionsAdded=False,
        individualApplicability=[dict(rule='UseProperClassLoader',line=343,status='NON_APPLICABLE_CONTEXT',
            reason='standalone host public JDK-interface proxy; not a JavaEE managed component'),
            dict(rule='UseConcurrentHashMap',line=351,status='NON_APPLICABLE_CONTEXT',
            reason='one fixture per sequential test, confined callback map; no thread/executor/parallel stream')],
        currentSourceTests=16,newTestIds=8,relatedRegressionMethods=8,suites=2,units=pt['units'],
        currentPtManifestSha256=pt_hash,forbiddenProductProbeHits=0,
        remaining='Repository exceptional/invalid-row branches and actual PostgreSQL contracts unexecuted; F03/451/native/CHR and QA051 held',
        productTestsReexecuted=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainClassesUnchanged=1843,newMethods=8,javaPaths=1802,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
