"""Bind non-adoption of duplicate/DB-substituting candidate; no target fixture or method is run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10358-scenario-media-contract-assessment-v1'
    assert not out.exists()
    normal = data.read_checked(data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json',
        'c7119960eb3cbf1514d58454c9f56e07780757339f4294d49ae82181acf24965')
    assert normal['source'] == 'b120eebab4bbe1f8d02c245a06e51e0783a616c5' and normal['actualExit'] == normal['testsExecuted'] == 0
    paths = ['src/schubert-nk-api/src/'+scope+'/java/dev/codex/schubert/nk/api/persistence/'+name+suffix+'.java'
        for scope,suffix in (('main','Repository'),('test','RepositoryTest')) for name in ('Scenario','Media')]
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    assert all(normal['begin']['inputHashes'][p] == h for p,h in hashes.items())
    for p in paths:
        if '/src/test/' in p:
            text = (data.ROOT/p).read_text()
            assert '@BeforeAll' in text and 'new ApiLogDatabaseFixture(root)' in text
    specs = ['evidence/01_PT/008_NK-SCN-001/001_NK-SCN-001_単体テスト仕様書.md',
        'evidence/01_PT/009_NK-MED-001/001_NK-MED-001_単体テスト仕様書.md',
        'evidence/01_PT/018_NK-OPS-001/2044_ScenarioMedia_SQL前境界依存判定.md']
    scenario = (data.ROOT/specs[0]).read_text()
    media = (data.ROOT/specs[1]).read_text()
    assert 'PostgreSQL18.6' in scenario and 'H2等へ代替しない' in scenario and '実PostgreSQL' in media
    assert all('PT-SCN-00'+str(n) in scenario for n in range(1,7)) and 'PT-MED-036' in media
    record = 'evidence/01_PT/018_NK-OPS-001/2057_ScenarioMedia正常JDBC契約の追加着手判定.md'
    verify(invocation)
    out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSourceHashes=hashes,referenceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in specs},
        humanDecision=record,humanDecisionSha256=data.sha((data.ROOT/record).read_bytes()),
        decision='CANDIDATE_NOT_ADOPTED_DUPLICATE_OR_UNQUALIFIED_SUBSTITUTE',
        newRequiredContractsFoundInReviewedScope=0,newFixturesCreated=0,newTargetTestsStarted=0,
        currentSourceSqlPtStatus='NOT_EXECUTED_HOLD',historicalRunsRevalidated=False,
        proxySubstituteAdopted=False,productTestsExecuted=0,externalActions=0,
        originalSourceOrBaselineModified=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
