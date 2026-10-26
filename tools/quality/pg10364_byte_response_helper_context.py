"""Freeze source-only helper review and its single identified oracle gap."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10364-byte-response-helper-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    names = {'h.golden','BackupArtifactFixture.golden','response','bytes'}
    selected = [r for r in sites if not r['sharedDirectMethodSelectors'] and names.intersection(r['expectedMethodSelectors'])]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert len(selected) == 110 and len(counts) == 23 and counts['MediaApplicationServiceTest'] == 17
    hashes = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    assert all(hashes[r['path']] == r['sourceSha256'] for r in selected)
    normal = data.read_checked(data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json',
        'c7119960eb3cbf1514d58454c9f56e07780757339f4294d49ae82181acf24965')
    assert all(normal['begin']['inputHashes'][p] == h for p,h in hashes.items())
    base = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'
    companions = [base+'media/MediaStageFixture.java',base+'media/MediaReplayFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java',
        'src/schubert-nk-batch/src/test/resources/backup/artifact-manifest.json']
    record = 'evidence/01_PT/018_NK-OPS-001/2059_直接byteResponse110site文脈レビュー結果.md'
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',selected)
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSites=110,sourceHashes=hashes,counts=dict(counts),allIndexSourceHashesUnchanged=True,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        companionHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        priorGoldenReview=dict(path='PG10362-golden-helper-context-v1/manifest.json',
            sha256='5082a9445528742cda2184924d73aae9cab2dbc7475fd73a1a314fc62362c6c6'),
        originalCompanionDescriptionErratum='2058 prose: three Java companion sources plus two JSON resources, not four Java',
        contextReviewOnly=True,automaticIndependenceVerdict=False,newDefectsIdentified=1,
        bug='BUG-1822',ykt='YKT-1573',productTestsExecuted=0,externalActions=0,newAccepted=0,
        wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
