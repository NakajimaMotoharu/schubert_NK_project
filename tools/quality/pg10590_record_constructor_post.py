"""Independent raw-line body hash and owner/source checks; no target evaluation."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10590-record-constructor-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10588-record-constructor-review-v1/manifest.json',
        '7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f')
    rows = data.read_checked(data.BASE/'PG10588-record-constructor-review-v1/constructor-reviews.json',primary['reviewsSha256'])
    bound = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/manifest.json',
        '5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1')
    bindings = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/constructor-bindings.json',bound['rowsSha256'])
    owners = {binding['owners'][0]:binding['mainSourceBinding'] for row in bindings
        for binding in row['assertionSpanConstructorBindings'].values() if binding['mainSourceBinding'] is not None}
    compact = 0
    for row in rows:
        assert all(row[k] == value for k,value in owners[row['owner']].items())
        raw = (data.ROOT/row['source']).read_bytes()
        assert data.sha(raw) == row['sourceSha256']
        review = row['review']
        if 'constructorBodySha256' not in review:
            continue
        lines = raw.decode().splitlines(keepends=True)
        first,last = review['constructorBodyStartLine'],review['constructorBodyEndLine']
        begin = sum(map(len,lines[:first-1]))+lines[first-1].rindex('{')+1
        end = sum(map(len,lines[:last-1]))+lines[last-1].index('}')
        assert data.sha(raw.decode()[begin:end].encode()) == review['constructorBodySha256']
        compact += 1
    assert len(rows) == len(owners) == 61 and compact == 53
    assert Counter(row['review']['kind'] for row in rows) == primary['constructorKinds']
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in primary['validationHelperHashes'].items())
    record = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2087_Main値constructor61型の本文・所有copy・例外oracleレビュー.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256='7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f',
        exactOwnerSourceRows=61,independentRawLineConstructorBodyHashes=53,
        constructorKinds=primary['constructorKinds'],humanReviewSha256=data.sha(record.read_bytes()),
        argumentOriginsAndFullCaseOraclesQualified=False,newGap='BUG-1846/YKT1597_FOUR_SITES',
        targetCompilation=0,targetClassLoading=0,productTestsExecuted=0,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
