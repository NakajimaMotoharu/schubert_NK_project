"""Bind the API42 human source review, not product execution or oracle certification."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f12718441140c670950760185b596ab5627377db'
COUNTS = dict(UserMutationRequestTest=2,UserQueryRequestTest=2,LogRequestTest=2,
    MediaApplicationServiceTest=1,MediaRequestTest=1,QuestionMutationApplicationServiceTest=2,
    QuestionMutationReplayServiceTest=2,QuestionQueryApplicationServiceTest=2,
    QuestionQueryRepositoryTest=1,QuestionQueryRequestTest=1,QuestionSubmitRequestTest=2,
    ScenarioApplicationServiceTest=1,PostgresDeploymentTest=1,InboxModelTest=1,
    OperationFingerprintTest=1,SecretBufferTest=2,AuthenticationInboxCleanupTest=1,
    InboxCleanupNonAuthenticationTest=1,InspectionParentBoundaryTest=1,
    ApiDurationMetricExporterTest=1,ApiObservationContextTest=1,AsyncJobCountRepositoryTest=1,
    AsyncJobMetricCollectorTest=1,OutboxObservationRepositoryTest=1,AuthContextCodecTest=1,
    AuthSessionServiceTest=1,LoginInboxServiceTest=1,LoginUsernameTest=2,
    PasswordPolicyTest=3,ApiApplicationPreparationTest=2)


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10276-api-shared-context-v1'
    assert not out.exists()
    prior = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',prior['sitesJsonSha256'])
    selected = [r for r in sites if r['sharedDirectMethodSelectors'] and 'schubert-nk-api/' in r['path']]
    assert len(selected) == 42 and Counter(Path(r['path']).stem for r in selected) == COUNTS
    hashes = {r['path']:r['sourceSha256'] for r in selected}
    assert len(hashes) == 30 and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    rows = []
    for r in selected:
        row = dict(r)
        lines = (data.ROOT/r['path']).read_text().splitlines()
        gap = Path(r['path']).stem == 'QuestionQueryApplicationServiceTest' and r['line'] == 258
        row.update(contextSha256=data.sha('\n'.join(lines[max(0,r['line']-18):r['line']+3]).encode()),
            verdict='TRANSITIVE_EXPECTED_PROFILE_DEPENDS_ON_SUT_BUG1811' if gap else
                'NO_DEFECT_IDENTIFIED_IN_REVIEWED_CONTEXT_NOT_SOLE_ORACLE_CERTIFICATION')
        rows.append(row)
    assert sum(r['verdict'].endswith('BUG1811') for r in rows) == 1
    record = 'evidence/01_PT/018_NK-OPS-001/2046_API共有selector42site文脈レビュー結果.md'
    content = (data.ROOT/record).read_text()
    assert all('|'+name+'|' in content for name in COUNTS)
    companions = [
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionQueryReplayServiceTest.java',
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioReplayFixture.java']
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        reviewedSites=42,sourceHashes=hashes,counts=COUNTS,remainingSharedSites=62,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        companionSourceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        noDefectIdentifiedContexts=41,oracleGapSites=1,bug='BUG-1811',ykt='YKT-1562',
        contextReviewOnly=True,automaticIndependenceVerdict=False,targetCodeExecuted=False,
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,
        formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
