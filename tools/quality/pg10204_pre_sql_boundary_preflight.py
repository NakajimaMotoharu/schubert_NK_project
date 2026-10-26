"""Freeze thirteen pre-try/pre-JDBC methods and their exact current physical classes."""
from collections import Counter
import json
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify

SOURCE = 'd4ba0fcbe8855b9674413d395b46d2de7bb2ded9'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10202-pre-sql-boundary-six-compile-v1/snapshot'
OUT = data.BASE/'PG10204-pre-sql-boundary-preflight-v1'
PREFIX = 'src/schubert-nk-api/src/test/java/'
CLASSES = {
    'dev.codex.schubert.nk.api.persistence.UserQueryPreSqlBoundaryTest':('ADM',4,'WBS-P010-01'),
    'dev.codex.schubert.nk.api.persistence.LogQueryPreSqlBoundaryTest':('LOG',3,'WBS-P010-04'),
    'dev.codex.schubert.nk.api.persistence.QuestionQueryPreSqlBoundaryTest':('QRY',6,'WBS-P014-01')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10202-pre-sql-boundary-six-compile-v1/manifest.json',
        'a050b88ec51ec64a18d0abd5adf5ea2bf64304a496735acb40f4da8091dfa8f2')
    old = data.read_checked(data.BASE/'PG10169-cancel-six-compile-v2/manifest.json',
        '1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    new_paths = {PREFIX+name.replace('.','/')+'.java' for name in CLASSES}
    assert set(hashes)-set(old['begin']['inputHashes']) == new_paths
    assert all(hashes[p] == h for p,h in old['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    cases,physical = [],{}
    for binary,(tag,count,owner) in CLASSES.items():
        path = PREFIX+binary.replace('.','/')+'.java'
        text = (NORMAL/path).read_text()
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods) == count
        assert not any(v in text for v in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir',
            '.prepareStatement(','.getAutoCommit(','.isReadOnly(','.executeQuery(','.close(',
            'DriverManager','DataSource','preserveFatal','ProcessBuilder','java.lang.foreign','System.getenv'))
        assert 'Proxy.newProxyInstance' in text and 'calls.incrementAndGet()' in text
        assert 'throw new AssertionError("unexpected JDBC access")' in text and 'assertEquals(0, calls.get())' in text
        target = NORMAL/'src/schubert-nk-api/target/test-classes'/(binary.replace('.','/')+'.class')
        matches = sorted(target.parent.glob(target.stem+'*.class'))
        assert {p.name for p in matches} == {target.name,target.stem+'$NoSql.class'}
        for p in matches:
            model = decode(p.read_bytes(),str(p.relative_to(NORMAL/'src/schubert-nk-api/target/test-classes')))
            assert model['sourceFile'] == Path(path).name
            physical[str(p)] = data.sha(p.read_bytes())
        model = decode(target.read_bytes(),binary.replace('.','/')+'.class')
        for index,method in enumerate(methods,1):
            assert len([m for m in model['methods'] if m['name'] == method and m['descriptor'] == '()V' and m['hasCode']]) == 1
            test_id = 'PT-'+tag+'-PRE'+str(index).zfill(3)
            assert test_id in text
            cases.append(dict(className=binary,method=method,path=path,sourceSha256=hashes[path],testId=test_id,canonicalOwner=owner))
    jar = Path(normal['jars']['api']['path'])
    with zipfile.ZipFile(jar) as archive:
        subjects = {n:data.sha(archive.read(n)) for n in archive.namelist() if n.endswith('.class') and
            any(n.startswith('dev/codex/schubert/nk/api/persistence/'+s) for s in ('UserQueryRepository','LogQueryRepository','QuestionQueryRepository'))}
    assert set(subjects) == {'dev/codex/schubert/nk/api/persistence/'+s+'.class' for s in
        ('UserQueryRepository','LogQueryRepository','QuestionQueryRepository','QuestionQueryRepository$RowMapper')}
    assert len(cases) == 13 and len(physical) == 6 and len({r['testId'] for r in cases}) == 13
    review = 'evidence/01_PT/018_NK-OPS-001/2036_SQL前境界の依存判定.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=len(cases),expectedSuites=len(CLASSES),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        normalManifestSha256='a050b88ec51ec64a18d0abd5adf5ea2bf64304a496735acb40f4da8091dfa8f2',
        physicalTestFiles=physical,physicalMainClasses=subjects,allCurrentSourceInputHashes=hashes,
        newSourceHashes={p:hashes[p] for p in sorted(new_paths)},allPreviousSourceInputHashesUnchanged=True,
        boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        expectedJdbcInvocations=0,heldSqlAndGraphExecutionPermitted=False,productTestsExecuted=0,newTestIds=13,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=len(cases),suites=len(CLASSES),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
