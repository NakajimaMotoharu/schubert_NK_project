"""Source-only role/code/hash oracle context binding, never target execution."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10390-role-code-hash-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in sites if not r['sharedDirectMethodSelectors'] and
        {'role.wireValue','code.wireValue','hash'}.intersection(r['expectedMethodSelectors'])]
    counts = Counter(Path(r['path']).stem for r in selected)
    assert len(selected) == 42 and len(counts) == 21
    normal = data.read_checked(data.BASE/'PG10378-media-literal-six-compile-v1/manifest.json',
        'c6862b046f1fae580ce0c8a3a07399f2cc2ca7d4657ca479c499ee6d80d4af9b')
    hashes = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    assert all(normal['begin']['inputHashes'][p] == h for p,h in hashes.items())
    rows = [dict(**r,currentSourceSha256=hashes[r['path']],
        originalLineApplicableToCurrentSource=hashes[r['path']] == r['sourceSha256']) for r in selected]
    matches = {}
    for selector,total,source_count in (('role.wireValue()',18,13),('code.wireValue()',15,6)):
        found = {}
        for module in ('api','web','batch','bootstrap'):
            for p in (data.ROOT/('src/schubert-nk-'+module+'/src/test')).rglob('*.java'):
                text = p.read_text()
                n = text.count(selector)
                if n:
                    rel = str(p.relative_to(data.ROOT))
                    digest = data.sha(p.read_bytes())
                    assert normal['begin']['inputHashes'][rel] == digest
                    found[rel] = dict(count=n,sha256=digest,
                        lines=[i for i,l in enumerate(text.splitlines(),1) if selector in l])
        assert len(found) == source_count and sum(r['count'] for r in found.values()) == total
        matches[selector] = found
    record = 'evidence/01_PT/018_NK-OPS-001/2061_RoleCodeHash42site文脈レビュー結果.md'
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSites=42,sourceHashes=hashes,counts=dict(counts),horizontalSourceMatches=matches,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        contextReviewOnly=True,automaticIndependenceVerdict=False,newDefectsIdentified=2,
        defects=['BUG-1825','BUG-1826'],horizontalReviews=['YKT-1576','YKT-1577'],
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
