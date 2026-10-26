"""Bind 62 public-source review contexts only; no target class or original fixture is run."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10290-remaining-shared-context-v1'
    assert not out.exists()
    prior = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',prior['sitesJsonSha256'])
    selected = [r for r in sites if r['sharedDirectMethodSelectors'] and 'schubert-nk-api/' not in r['path']]
    assert len(selected) == 62
    record = 'evidence/01_PT/018_NK-OPS-001/2047_残共有selector62site文脈レビュー結果.md'
    review = (data.ROOT/record).read_text()
    declared = dict((name,int(n)) for name,n in re.findall(r'^\|([A-Za-z0-9]+Test)\|(\d+)\|',review,re.M))
    counts = Counter(Path(r['path']).stem for r in selected)
    assert counts == declared and len(counts) == 36 and sum(counts.values()) == 62
    hashes = {r['path']:r['sourceSha256'] for r in selected}
    assert len(hashes) == 36 and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    rows = []
    for r in selected:
        lines = (data.ROOT/r['path']).read_text().splitlines()
        rows.append(dict(**r,contextSha256=data.sha('\n'.join(lines[max(0,r['line']-18):r['line']+3]).encode()),
            verdict='NO_DEFECT_IDENTIFIED_IN_REVIEWED_CONTEXT_NOT_SOLE_ORACLE_CERTIFICATION'))
    companions = [
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryReceiptFixture.java',
        'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceCredentialSetTest.java']
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source='21228608b9defca3eb6fac7e0485f28a56925246',
        invocation=invocation,reviewedSites=62,reviewedSources=36,sourceHashes=hashes,counts=dict(counts),
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),
        companionSourceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in companions},
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        contextReviewOnly=True,automaticIndependenceVerdict=False,newConfirmedOracleDefects=0,
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,
        formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
