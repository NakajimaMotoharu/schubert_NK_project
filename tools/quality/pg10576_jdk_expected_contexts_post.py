"""Independent raw-span original metadata post; never invoke consumer or Product."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span

OUT = data.BASE/'PG10576-jdk-expected-contexts-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10574-jdk-expected-contexts-v1/manifest.json',
        'e6444600194163bafccbd61dbb6c77f0cd1122ab12bd627cfaa01b9128a5a819')
    rows = data.read_checked(data.BASE/'PG10574-jdk-expected-contexts-v1/reviewed-sites.json',primary['reviewedSitesSha256'])
    original = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    originals = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',original['sitesJsonSha256'])
    key = lambda row:tuple(row[k] for k in ('path','method','line','expectedExpressionSha256'))
    index = {key(row):row for row in originals}
    for row in rows:
        old = index[key(row)]
        assert all(row[k] == value for k,value in old.items())
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256']
        matching_span(text,row)
    assert len(rows) == 104 and len({row['path'] for row in rows}) == 33
    counts = Counter(row['contextReviewCategory'] for row in rows)
    assert counts == primary['counts'] and counts['PRIOR_STATIC_CONTEXT_REFERENCE_NOT_NEW'] == 38
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in primary['companionHashes'].items())
    assert not primary['automaticIndependenceVerdict'] and not primary['wholeCaseFixtureCorrectnessAccepted']
    record = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2085_JDK期待式104箇所・既文脈参照と相関検査の分離.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256='e6444600194163bafccbd61dbb6c77f0cd1122ab12bd627cfaa01b9128a5a819',
        originalMetadataFieldsRetained=104,independentOriginalRawExpressionSpansMatched=104,
        consumerSources=33,counts=dict(counts),companionHashesUnchanged=True,
        humanReviewSha256=data.sha(record.read_bytes()),relativeRecord=str(record.relative_to(data.ROOT)),
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        fullOracleQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
