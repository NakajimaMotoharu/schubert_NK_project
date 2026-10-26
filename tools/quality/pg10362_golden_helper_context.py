"""Bind a human review of 65 golden-selector sites; never execute target tests."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10362-golden-helper-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in sites if 'golden' in r['expectedMethodSelectors'] and not r['sharedDirectMethodSelectors']]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert counts == dict(ScenarioApplicationServiceTest=11,OutboxFailureOwnershipTest=1,
        LogQueryRepositoryTest=2,LoginReplayServiceTest=7,LogoutInboxServiceTest=20,BackupDatabaseCopyTest=7,
        BackupManifestCodecTest=2,BackupManifestReaderTest=3,QuestionSubmitFormTest=5,UserCreateFormTest=3,
        UserMutationFormTest=4) and len(selected) == 65
    current = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    assert all(current[r['path']] == r['sourceSha256'] for r in selected)
    normal = data.read_checked(data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json',
        'c7119960eb3cbf1514d58454c9f56e07780757339f4294d49ae82181acf24965')
    assert normal['source'] == 'b120eebab4bbe1f8d02c245a06e51e0783a616c5'
    assert all(normal['begin']['inputHashes'][p] == h for p,h in current.items())
    companions = [
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioReplayFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java',
        'src/schubert-nk-batch/src/test/resources/backup/manifest-golden.json',
        'src/schubert-nk-batch/src/test/resources/backup/artifact-manifest.json']
    record = 'evidence/01_PT/018_NK-OPS-001/2058_Golden直接helper65site文脈レビュー結果.md'
    content = (data.ROOT/record).read_text()
    assert all('|'+name+'|'+str(n)+'|' in content for name,n in counts.items())
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',selected)
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSites=65,sourceHashes=current,counts=dict(counts),allIndexSourceHashesUnchanged=True,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        companionHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        contextReviewOnly=True,automaticIndependenceVerdict=False,newDefectsIdentified=0,
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,
        formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
