"""Bind70 existing expected helper sites to reviewed source; never execute target fixtures."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10308-expected-helper-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in sites if 'expected' in r['expectedMethodSelectors'] and not r['sharedDirectMethodSelectors']]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert len(selected) == 70 and counts == dict(UserQueryApplicationServiceTest=15,
        LogQueryApplicationServiceTest=18,QuestionMutationApplicationServiceTest=13,
        QuestionQueryApplicationServiceTest=14,LoginInboxServiceTest=10)
    old_post = data.read_checked(data.BASE/'PG10287-query-wire-oracle-source-post-v2/manifest.json',
        'f6c380e1e7a6971e8b79eaf6da9b5df25b4efdee65c206cf3b91ef4028e29fb3')
    post = data.read_checked(data.BASE/'PG10304-query-test-literal-post-v1/manifest.json',
        'f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904')
    assert old_post['actualExit'] == post['actualExit'] == 0
    hashes = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    rows = []
    for row in selected:
        stem = Path(row['path']).stem
        changed = row['sourceSha256'] != hashes[row['path']]
        if changed:
            assert stem == 'QuestionQueryApplicationServiceTest' and post['sourceHashes'][row['path']] == hashes[row['path']]
            assert old_post['allOriginalAssertionsPreserved'] and post['allOriginalAssertionsPreserved']
        verdict = ('TRANSITIVE_PROFILE_ORACLE_GAP_BUG1814' if stem == 'UserQueryApplicationServiceTest' else
            'PREVIOUS_BUG1811_FIXED_SOURCE_PRESERVATION_NOT_NEW_PROGRESS' if changed else
            'NO_DEFECT_IDENTIFIED_IN_REVIEWED_CONTEXT_NOT_SOLE_ORACLE_CERTIFICATION')
        rows.append(dict(**row,currentSourceSha256=hashes[row['path']],verdict=verdict,
            originalLineAppliesToCurrentSource=not changed,
            changedSourceBinding='PG10287+PG10304 exact original assertion/token preservation' if changed else None))
    record = 'evidence/01_PT/018_NK-OPS-001/2049_Expected直接helper70site文脈レビュー結果.md'
    review = (data.ROOT/record).read_text()
    assert all('|'+name+'|'+str(n)+'|' in review for name,n in counts.items())
    companions = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/'+p for p in (
        'application/admin/UserQueryReplayServiceTest.java','application/log/LogVectors.java',
        'security/LoginReplayServiceTest.java')]
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source='4c975c3eb1d8d5540805fae642b80d0d5e781c12',
        invocation=invocation,reviewedSites=70,sourceHashes=hashes,counts=dict(counts),
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        companionSourceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        newGapSites=15,newSharedHelperGaps=1,previousFixedGapSitesNotNew=14,noDefectIdentifiedSites=41,
        contextReviewOnly=True,automaticIndependenceVerdict=False,productTestsExecuted=0,externalActions=0,
        newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None,bug='BUG-1814',ykt='YKT-1565'))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
