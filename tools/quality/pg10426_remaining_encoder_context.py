"""Bind 24 remaining encoder-like source contexts and exact expected/actual classification."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10426-remaining-encoder-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    pattern = re.compile(r'(wireValue|encode|decode|fromWire|fields|Codec|normalize)')
    selected = [r for r in sites if not r['sharedDirectMethodSelectors'] and
        any(pattern.search(m) for m in r['expectedMethodSelectors']) and
        not {'role.wireValue','code.wireValue'}.intersection(r['expectedMethodSelectors'])]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert len(selected) == 24 and len(counts) == 14
    normal = data.read_checked(data.BASE/'PG10414-result-code-six-compile-v1/manifest.json',
        '83e2904ee2a0ee50ef0efab4916f73f53aaa0660cd8b3a2555b2eec21477da35')
    hashes = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    assert all(normal['begin']['inputHashes'][p] == h for p,h in hashes.items())
    rows = [dict(**r,currentSourceSha256=hashes[r['path']],
        originalLineApplicableToCurrentSource=hashes[r['path']] == r['sourceSha256']) for r in selected]
    state,authority,actual = {},{},{}
    for module in ('api','web','batch','bootstrap'):
        for path in (data.ROOT/('src/schubert-nk-'+module+'/src/test')).rglob('*.java'):
            text = path.read_text()
            rel = str(path.relative_to(data.ROOT))
            for needle,destination in [('state.wireValue()',state),('"ROLE_" + p.role().wireValue()',authority)]:
                n = text.count(needle)
                if n:
                    digest = data.sha(path.read_bytes())
                    assert normal['begin']['inputHashes'][rel] == digest
                    destination[rel] = dict(count=n,sha256=digest,
                        lines=[i for i,l in enumerate(text.splitlines(),1) if needle in l])
            if 'p.role().wireValue()' in text and rel not in authority:
                assert path.name in {'SessionFormLoginTest.java','WebSecurityChainTest.java'}
                assert 'assertEquals(n % 2 == 0 ? "USER" : "ADMIN", p.role().wireValue());' in text
                actual[rel] = dict(count=text.count('p.role().wireValue()'),sha256=data.sha(path.read_bytes()))
    assert len(state) == 2 and sum(r['count'] for r in state.values()) == 8
    assert len(authority) == 6 and sum(r['count'] for r in authority.values()) == 7
    assert len(actual) == 2 and sum(r['count'] for r in actual.values()) == 2
    base = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'
    companions = [base+'logging/WebLogPayloadCodecTest.java',base+'session/SessionAttributeCodecTest.java']
    record = 'evidence/01_PT/018_NK-OPS-001/2064_残encoder24site文脈レビュー結果.md'
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSites=24,sourceHashes=hashes,counts=dict(counts),
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        stateExpectedAndFixtureSourceMatches=state,authorityExpectedAndFixtureSourceMatches=authority,
        actualSideAssertionsNotToModify=actual,companionHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        contextReviewOnly=True,automaticIndependenceVerdict=False,newDefectsIdentified=2,
        defects=['BUG-1829','BUG-1830'],horizontalReviews=['YKT-1580','YKT-1581'],
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
