"""Independent literal-spec/current-declaration join; no ownership or dynamic qualification inference."""
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10942-cross-owner-current-post-v1'
SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
SPEC = 'evidence/01_PT/018_NK-OPS-001/1936_G13CrossMethod23_TestID・責任対応仕様.md'


def contract(rows,expected,hashes):
    if len(rows) != len(expected) or len({(r['path'],r['method']) for r in rows}) != len(expected):
        raise ValueError('unique complete existing method set')
    for row in rows:
        key = (row['path'],row['method'])
        value = expected.get(key)
        if value is None or any(row[k] != v for k,v in value.items()):
            raise ValueError('literal original responsibility and family mapping')
        if row['source'] != SOURCE or row['sourceSha256'] != hashes[row['path']]:
            raise ValueError('current input, not historical source')
        if row['canonicalFileOwner'] != 'UNKNOWN' or row['canonicalFileCostOwner'] != 'UNKNOWN':
            raise ValueError('no file-level owner guess')
        if row['additionalSharedCostPp'] != 0 or row['oldRuntimeReassigned'] or row['currentPtQualified']:
            raise ValueError('no allocation or transferred qualification')
        if row['declarationCheck'] != 'EXACT_CURRENT_NAME_ARITY_ONLY_NOT_AST_OR_CALLEE':
            raise ValueError('bounded declaration-only scope')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10940-cross-owner-current-declarations-v1/manifest.json'
    primary = data.read_checked(path,'d9c12d311bfb7d7aa8168aff6f131c003b5b53d7de5eb2a1c7196eda05f945bc')
    assert primary['actualExit'] == 0 and primary['source'] == SOURCE
    rows = data.read_checked(path.parent/'method-bindings.json',primary['methodBindingsSha256'])
    raw = (data.ROOT/SPEC).read_bytes()
    assert data.sha(raw) == 'c87fe5eb73645d2f8a0055ffc8d7cc65bf8d0ceff68b61d8552ba85a94209aef'
    paths = {('API' if '/schubert-nk-api/' in r['path'] else 'WEB'):r['path'] for r in rows}
    expected = {}
    for line in raw.decode().splitlines():
        if not line.startswith(('|API|','|WEB|')):
            continue
        _,label,method,ids,business,mains,note,_ = line.split('|')
        key = (paths[label],method)
        assert key not in expected
        expected[key] = dict(existingTestFamilies=ids.split(','),businessContractWbs=business.split(','),
            reviewedMainSubjects=dict(p.split(':') for p in mains.split(',')),independentOracleReference=note)
    assert len(expected) == 23 and sum(len(r['existingTestFamilies']) for r in expected.values()) == 34
    assert len({x for r in expected.values() for x in r['existingTestFamilies']}) == 26
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths.values()}
    for p in paths.values():
        text = (data.ROOT/p).read_text()
        lines = text.splitlines()
        declarations = []
        for i,line in enumerate(lines):
            if line.strip() == '@Test':
                declaration = re.fullmatch(r'  void (\w+)\(\)(?: throws [A-Za-z, ]+)? \{',lines[i+1])
                assert declaration is not None
                declarations.append(declaration.group(1))
        assert len(declarations) == len(set(declarations))
        assert set(declarations) == {name for path_key,name in expected if path_key == p}
    contract(rows,expected,hashes)
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','old'),('canonicalFileOwner','WBS-P004-05'),
                        ('canonicalFileCostOwner','WBS-G13.07'),('existingTestFamilies',['invented']),
                        ('businessContractWbs',['WBS-G13.07']),('additionalSharedCostPp',1),
                        ('oldRuntimeReassigned',True),('currentPtQualified',True),('declarationCheck','AST_RESOLVED')]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,expected,hashes)
        except ValueError:
            pass
        else:
            raise AssertionError('forged responsibility or dynamic credit accepted')
    for p,digest in primary['metadataGuardHashes'].items():
        assert data.sha((data.ROOT/p).read_bytes()) == digest
    assert primary['unknownPrimaryFiles'] == 2 and primary['registered'] == 1808
    assert primary['productTestsExecuted'] == primary['externalActions'] == primary['newAccepted'] == 0
    assert primary['coverage'] is None and not primary['oldRuntimeReassigned'] and not primary['wholeG13Accepted']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),methodBindingsSha256=primary['methodBindingsSha256'],
        independentSpecSha256=data.sha(raw),methodDeclarations=23,existingFamilies=26,existingRelations=34,
        metadataNegativeVectors=len(bads),unknownPrimaryFiles=2,registered=1808,javaPaths=1810,
        oldRuntimeReassigned=False,currentPtQualified=False,productTestsExecuted=0,coverage=None,
        newAccepted=0,wholeG13Accepted=False,externalActions=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
