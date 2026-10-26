"""Read fixed public protocol/storage syntax only; never invoke product code or claim oracle PASS."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

SOURCE = 'dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77'
ROOT = data.ROOT
NORMAL = ROOT.parent/'pgpt-runs/PG379/pg10100-query-batch-six-compile-v1/snapshot'
SLOT = ROOT.parent/'pgpt-runs/PG379/pg10120-protocol-storage-oracle-sites-v1'
OUT = data.BASE/'PG10120-protocol-storage-oracle-sites-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json',
        'a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    selected = {p:h for p,h in normal['begin']['inputHashes'].items()
        if re.fullmatch(r'src/schubert-nk-(protocol|storage)/src/test/java/[A-Za-z0-9_$/]+\.java',p)}
    modules = Counter(p.split('/')[1] for p in selected)
    assert modules == {'schubert-nk-protocol':23,'schubert-nk-storage':29} and len(selected) == 52
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in selected.items())
    helper = ROOT/'tools/quality/architecture/AssertionExpectedSyntaxInventory.java'
    helper_sha = data.sha(helper.read_bytes())
    assert all(marker not in helper.read_text() for marker in ('.analyze(','.generate(','Class.forName','setAccessible','getDeclared'))
    SLOT.mkdir(mode=0o700)
    reader = SLOT/'reader'
    reader.mkdir()
    listing = SLOT/'fixed-source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(p+'\n' for p in sorted(selected)))
    listing_sha = data.sha(listing.read_bytes())
    tc = ROOT.parent/'toolchain'
    steps.SLOT = SLOT
    stages = [steps.step('compile-syntax-tool',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25',
        '-proc:none','-Xlint:all','-Werror','-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('parse-assertion-sites',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader),
        helper.stem,str(NORMAL),str(listing)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    raw = (SLOT/'parse-assertion-sites.stdout').read_bytes()
    lines = raw.decode('utf-8').splitlines()
    assert lines[0] == 'METADATA_VECTORS\t6'
    summary = lines[-1].split('\t')
    assert len(summary) == 3 and summary[:2] == ['SUMMARY','52']
    rows = []
    for line in lines[1:-1]:
        parts = line.split('\t')
        assert len(parts) == 10
        path,method,number,assertion,kind,expected,actual,constructors,shared,digest = parts
        assert path in selected and re.fullmatch('[0-9a-f]{64}',digest)
        assert assertion in {'assertEquals','assertArrayEquals','assertSame','assertNotEquals'}
        assert re.fullmatch('[A-Z_]+',kind) and 1 <= int(number) <= len((NORMAL/path).read_text().splitlines())
        expected = expected.split(';') if expected else []
        actual = actual.split(';') if actual else []
        constructors = constructors.split(';') if constructors else []
        assert int(shared) == len(set(expected)&set(actual))
        rows.append(dict(path=path,sourceSha256=selected[path],method=method,line=int(number),
            assertion=assertion,expectedAstKind=kind,expectedMethodSelectors=expected,
            actualMethodSelectors=actual,expectedConstructorTypes=constructors,
            sharedDirectMethodSelectors=int(shared),expectedExpressionSha256=digest,
            qualification='SYNTAX_CANDIDATE_ONLY_NOT_INDEPENDENCE_VERDICT'))
    assert len(rows) == int(summary[2]) and rows
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in selected.items())
    assert data.sha(helper.read_bytes()) == helper_sha and data.sha(listing.read_bytes()) == listing_sha
    verify(invocation)
    OUT.mkdir()
    (OUT/'assertion-sites.tsv').write_bytes(raw)
    data.write(OUT/'sites.json',rows)
    counts = dict(sites=len(rows),directExpectedCalls=sum(bool(r['expectedMethodSelectors']) for r in rows),
        sameDirectSelectorBothSides=sum(bool(r['sharedDirectMethodSelectors']) for r in rows),
        expectedIdentifier=sum(r['expectedAstKind']=='IDENTIFIER' for r in rows),
        expectedConstructor=sum(bool(r['expectedConstructorTypes']) for r in rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        selectedSources=52,sourceHashes=selected,modules=dict(modules),helperSha256=helper_sha,
        sourceListSha256=listing_sha,metadataSyntaxVectors=6,**counts,
        tsvSha256=data.sha(raw),sitesJsonSha256=data.sha((OUT/'sites.json').read_bytes()),
        qualification='SYNTAX_SITE_DIAGNOSTIC_NOT_ORACLE_PASS',variableDependencyResolved=False,
        targetClassesLoaded=False,processorsInvoked=False,productTestsExecuted=0,externalActions=0,
        actualNativeActions=0,actualDbActions=0,newAccepted=0,wholeG03Accepted=False,
        formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,**counts,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
