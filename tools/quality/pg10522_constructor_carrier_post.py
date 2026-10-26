"""Independent original-byte span/hash binding; no Java, fixture or target invocation."""
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10522-constructor-carrier-post-v1'
PIN = 'de115abc7337ea95939b3fc80360882f250b5d3b977596b179c815a6590afa23'


def matching_span(text,row):
    lines = text.splitlines(keepends=True)
    start = sum(map(len,lines[:row['line']-1]))
    end = start+len(lines[row['line']-1])
    matches = []
    # Independent of the primary lexer/delimiter stack: original AST byte digest
    # identifies the expression among raw source spans ending before a comma.
    for begin in range(start,end):
        if text[begin].isspace():
            continue
        for delimiter in re.finditer(',',text[begin:begin+5000]):
            finish = begin+delimiter.start()
            expression = text[begin:finish].rstrip()
            if data.sha(expression.encode()) == row['expectedExpressionSha256']:
                matches.append((begin,begin+len(expression)))
    if len(matches) != 1:
        raise ValueError('one immutable original expression digest required')
    return matches[0]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/manifest.json',PIN)
    rows = data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/sites.json',primary['sitesSha256'])
    original = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    originals = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',original['sitesJsonSha256'])
    index = {(r['path'],r['method'],r['line'],r['expectedExpressionSha256']):r for r in originals}
    assert subprocess.check_output(['git','diff','--name-only',primary['source'],'--','src'],cwd=data.ROOT) == b''
    for row in rows:
        old = index[(row['path'],row['method'],row['line'],row['expectedExpressionSha256'])]
        assert all(row[k] == value for k,value in old.items())
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256']
        matching_span(text,row)
    assert len(rows) == 128 and len({r['path'] for r in rows}) == 21
    assert sum(not r['unresolvedArgumentNames'] for r in rows) == 100
    assert sum(bool(r['additionalConstructorTypesNotReviewed']) for r in rows) == 5
    sample = 'assertEquals(\n new CleanupCounts(1, 1, 0), actual);'
    row = dict(line=2,expectedExpressionSha256=data.sha(b'new CleanupCounts(1, 1, 0)'))
    assert matching_span(sample,row)
    rejected = 0
    for bad in (dict(row,line=1),dict(row,expectedExpressionSha256='0'*64)):
        try:
            matching_span(sample,bad)
        except ValueError:
            rejected += 1
    assert rejected == 2
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=PIN,originalAstMetadataRetained=True,independentRawSpanDigestMatches=128,
        unchangedConsumerSources=21,explicitLiteralEnumArgumentSites=100,variableArgumentSites=28,
        additionalConstructorSitesNotReviewed=5,rawSpanNegativeVectors=2,
        argumentProvenanceFullyResolved=False,wholeOracleIndependenceAccepted=False,
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
