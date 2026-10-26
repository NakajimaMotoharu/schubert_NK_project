"""Freeze twenty-two pre-try/pre-JDBC methods and their exact current physical classes."""
from collections import Counter
import json
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify

SOURCE = 'f12718441140c670950760185b596ab5627377db'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10263-scenario-media-six-compile-v2/snapshot'
OUT = data.BASE/'PG10262-scenario-media-boundary-preflight-v1'
PREFIX = 'src/schubert-nk-api/src/test/java/'
CLASSES = {
    'dev.codex.schubert.nk.api.persistence.ScenarioPreSqlBoundaryTest':('SCN',9,'WBS-P008-01'),
    'dev.codex.schubert.nk.api.persistence.MediaPreSqlBoundaryTest':('MED',13,'WBS-P009-01')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10263-scenario-media-six-compile-v2/manifest.json',
        '52622b296c357e6dabb76957c15978a1430b4d928887b0785f41d18ece977558')
    old = data.read_checked(data.BASE/'PG10226-header-profile-six-compile-v1/manifest.json',
        'ffb1b71ad14efa4b8921c58a19541728243e35d60f873983528bce177b914b9c')
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
            any(n.startswith('dev/codex/schubert/nk/api/persistence/'+s) for s in ('ScenarioRepository','MediaRepository'))}
    assert set(subjects) == {'dev/codex/schubert/nk/api/persistence/'+s+'.class' for s in
        ('ScenarioRepository','ScenarioRepository$RowMapper','MediaRepository','MediaRepository$RowMapper')}
    assert len(cases) == 22 and len(physical) == 4 and len({r['testId'] for r in cases}) == 22
    review = 'evidence/01_PT/018_NK-OPS-001/2044_ScenarioMedia_SQL前境界依存判定.md'
    failed = data.read_checked(data.BASE/'PG10260-scenario-media-six-compile-v1/manifest.json',
        'a8a30b3ffb1c61b1330b2edb882eca3005226a826c981fe691e26a7896412b27')
    assert failed['actualExit'] == failed['terminal']['actualExit'] == 1 and failed['testsExecuted'] == 0 and len(failed['jars']) == 3
    initial = data.read_checked(data.BASE/'PG10258-scenario-media-boundary-static-v1/manifest.json',
        '934b284ce3ac64b042732e1ef96ade160bd76a70919caf07f78105a0c7fac043')
    failed_root = data.ROOT.parent/'pgpt-runs/PG379/pg10260-scenario-media-six-compile-v1/snapshot'
    drafts = {}
    for path in sorted(new_paths):
        original = (failed_root/path).read_bytes()
        assert data.sha(original) == failed['begin']['inputHashes'][path]
        draft = original.replace(b'import dev.codex.schubert.nk.api.domain.Role;\nimport dev.codex.schubert.nk.api.security.AuthenticatedActor;',
            b'import dev.codex.schubert.nk.api.security.AuthenticatedActor;\nimport dev.codex.schubert.nk.api.security.Role;')
        assert data.sha(draft) == initial['sourceHashes'][path]
        drafts[path] = draft
    verify(invocation)
    OUT.mkdir()
    draft_out = OUT/'initial-draft'
    draft_out.mkdir()
    for path,raw in drafts.items(): (draft_out/(Path(path).name+'.txt')).write_bytes(raw)
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=len(cases),expectedSuites=len(CLASSES),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        normalManifestSha256='52622b296c357e6dabb76957c15978a1430b4d928887b0785f41d18ece977558',
        physicalTestFiles=physical,physicalMainClasses=subjects,allCurrentSourceInputHashes=hashes,
        newSourceHashes={p:hashes[p] for p in sorted(new_paths)},allPreviousSourceInputHashesUnchanged=True,
        boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        originalDraftSourceHashes={p:data.sha(raw) for p,raw in drafts.items()},
        initialDraftImportCorrection='security.Role to existing domain.Role before first compiler; original static hashes and reconstructed exact drafts preserved',
        failedCompileManifestSha256='a8a30b3ffb1c61b1330b2edb882eca3005226a826c981fe691e26a7896412b27',
        expectedJdbcInvocations=0,heldSqlAndGraphExecutionPermitted=False,productTestsExecuted=0,newTestIds=len(cases),
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=len(cases),suites=len(CLASSES),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
