"""54 existing wire assertions: bind review and previous profile fixes, not target execution."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10330-wire-helper-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in sites if 'wire' in r['expectedMethodSelectors'] and not r['sharedDirectMethodSelectors']]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert counts == dict(UserMutationReplayServiceTest=10,UserQueryReplayServiceTest=10,LogReplayServiceTest=10,
        MediaReplayServiceTest=6,QuestionMutationReplayServiceTest=2,QuestionQueryReplayServiceTest=6,
        ScenarioReplayServiceTest=9,ResultBoundResponseSnapshotCodecTest=1) and len(selected) == 54
    bindings = [
        ('PG10287-query-wire-oracle-source-post-v2','f6c380e1e7a6971e8b79eaf6da9b5df25b4efdee65c206cf3b91ef4028e29fb3'),
        ('PG10304-query-test-literal-post-v1','f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904'),
        ('PG10320-user-query-oracle-post-v1','3d06dba306747ab6039845c106e185e103102fd4d441ac257f684eb66cdb0d36')]
    verified = [data.read_checked(data.BASE/run/'manifest.json',digest) for run,digest in bindings]
    assert all(v['actualExit'] == 0 for v in verified)
    current = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    rows = []
    for r in selected:
        stem = Path(r['path']).stem
        changed = current[r['path']] != r['sourceSha256']
        if changed:
            assert stem in {'UserQueryReplayServiceTest','QuestionQueryReplayServiceTest'}
            assert any(v['sourceHashes'].get(r['path']) == current[r['path']] for v in verified)
        verdict = ('PREVIOUS_PROFILE_FIX_NOT_NEW_PROGRESS' if changed else
            'EXPECTED_SUCCESS_PROFILE_SHARED_WITH_SUT_BUG1817' if stem == 'QuestionMutationReplayServiceTest' else
            'NO_DEFECT_IDENTIFIED_IN_REVIEWED_WIRE_CONTEXT_NOT_SOLE_ORACLE_CERTIFICATION')
        rows.append(dict(**r,currentSourceSha256=current[r['path']],originalLineAppliesToCurrentSource=not changed,verdict=verdict))
    matches = {}
    for module in ('api','web','batch','bootstrap'):
        for p in (data.ROOT/('src/schubert-nk-'+module+'/src/test')).rglob('*.java'):
            n = p.read_text().count('code.usesSuccessProfile()')
            if n: matches[str(p.relative_to(data.ROOT))] = dict(count=n,sha256=data.sha(p.read_bytes()))
    assert len(matches) == 5 and sum(r['count'] for r in matches.values()) == 12
    companions = [data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application'/p for p in
        ('media/MediaReplayFixture.java','log/LogVectors.java','scenario/ScenarioReplayFixture.java')]
    record = 'evidence/01_PT/018_NK-OPS-001/2051_Wire直接helper54site文脈レビュー結果.md'
    content = (data.ROOT/record).read_text()
    assert all('|'+name+'|'+str(n)+'|' in content for name,n in counts.items())
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source='8788668513552ce50862797cb700d2b7a4162ac1',
        invocation=invocation,reviewedSites=54,sourceHashes=current,counts=dict(counts),
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),previousSourceProofBindings=bindings,
        companionSourceHashes={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in companions},
        positiveProfileSharedClassifierSources=matches,positiveProfileSharedClassifierCalls=12,
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        previousFixedSitesNotNew=16,gapWireSites=2,otherWireContextsNoDefectIdentified=36,
        contextReviewOnly=True,automaticIndependenceVerdict=False,productTestsExecuted=0,externalActions=0,
        newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None,bug='BUG-1817',ykt='YKT-1568'))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
