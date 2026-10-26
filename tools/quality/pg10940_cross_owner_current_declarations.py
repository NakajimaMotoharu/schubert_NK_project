"""Bind an existing cross-business method map to current declarations; preserve unknown file cost."""
from collections import Counter
import copy
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10940-cross-owner-current-declarations-v1'
OLD = data.BASE/'PG9554-cross-method23-source-ast-v1'
POST = data.BASE/'PG9556-cross-method23-bytecode-post-v1'
PMO = 'documents/400_PGPT/470_PMO/'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(OLD/'manifest.json','1894885ded2b7d5bab5fc3ee741a8ea2bb0b1bc49665b5417c62158c01224f78')
    post = data.read_checked(POST/'manifest.json','2cc03ca10c43b89096412104dc411de72e7d44a6390fb9f3c6e040e93c735fb1')
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    registry = data.read_checked(data.BASE/'PG10904-web-boundary-trace-v1/manifest.json',
        '51d41f21df6fc652f1ed093b507b4d205dbbce2c74d904e71c476dae28679e85')
    assert old['actualExit'] == post['actualExit'] == normal['actualExit'] == 0
    assert normal['source'] == registry['source'] == SOURCE != old['source'] == post['source']
    methods = data.read_checked(OLD/'method-trace.json',old['methodTraceSha256'])
    proofs = data.read_checked(POST/'main-owner-proofs.json',post['mainOwnerProofsSha256'])
    hashes = normal['begin']['inputHashes']
    guarded = {PMO+n:data.sha((data.ROOT/PMO/n).read_bytes()) for n in (
        '481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')}
    logical = {r['path']:r for r in data.read_checked(data.ROOT/(PMO+'485_WBS網羅性・受入対応.json'),
        guarded[PMO+'485_WBS網羅性・受入対応.json'])['artifacts']}
    assert len(logical) == 941 and len(methods) == 23 and len(proofs) == 7
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    paths = sorted({r['path'] for r in methods})
    assert paths == registry['unregisteredJavaPaths'] and len(paths) == 2
    rows, files = [],[]
    for path in paths:
        raw = (data.ROOT/path).read_bytes()
        names = re.findall(r'(?m)^  @Test\s*\n  void ([A-Za-z][A-Za-z0-9_]*)\(\)(?: throws [A-Za-z, ]+)? \{',raw.decode())
        previous = [r for r in methods if r['path'] == path]
        assert len(names) == len(set(names)) == len(previous) and set(names) == {r['method'] for r in previous}
        assert data.sha(raw) == hashes[path] != old['inputHashes'][path]
        for row in previous:
            bound = copy.deepcopy(row)
            bound.update(source=SOURCE,sourceSha256=hashes[path],historicalSourceSha256=row['sourceSha256'],
                historicalDeclarationLines=[row['startLine'],row['endLine']],declarationCheck='EXACT_CURRENT_NAME_ARITY_ONLY_NOT_AST_OR_CALLEE',
                canonicalFileOwner='UNKNOWN',canonicalFileCostOwner='UNKNOWN',additionalSharedCostPp=0,
                oldRuntimeReassigned=False,currentPtQualified=False)
            bound.pop('startLine');bound.pop('endLine')
            rows.append(bound)
        files.append(dict(path=path,sourceSha256=hashes[path],methods=len(names),canonicalOwner='UNKNOWN',
            canonicalCostOwner='UNKNOWN',reason='MULTIPLE_EXISTING_BUSINESS_OWNERS_NO_DOCUMENTED_FILE_COST_RULE',
            currentPtQualified=False))
    owners = []
    for path,proof in proofs.items():
        original = logical[path]
        assert original['owner'] == original['costOwner'] == proof['owner']
        owners.append(dict(path=path,canonicalOwner=original['owner'],canonicalCostOwner=original['costOwner'],
            historicalSha256=proof['sourceSha256'],currentSha256=hashes[path],oldRuntimeReassigned=False))
    introductions = {}
    for path,commit in zip(paths,('ac5f4d6c7115ae25f6c7e46e05589c0842deb94b','ca0afe41b1273b8624bcb6bcb0a7f05f7cccde9d')):
        first = subprocess.check_output(['git','show',commit+':'+path],cwd=data.ROOT)
        introductions[path] = dict(commit=commit,originalSha256=data.sha(first))
    assert Counter(r['path'] for r in rows) == Counter({paths[0]:9,paths[1]:14})
    assert sum(len(r['existingTestFamilies']) for r in rows) == 34
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in {**hashes,**guarded}.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'method-bindings.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,files=files,mainOwners=owners,
        historicalSource=old['source'],introductions=introductions,methodBindingsSha256=data.sha((OUT/'method-bindings.json').read_bytes()),
        metadataGuardHashes=guarded,methods=23,relations=34,registered=1808,javaPaths=1810,unknownPrimaryFiles=2,
        oldRuntimeReassigned=False,wholeG13Accepted=False,whole451Accepted=False,newAccepted=0,
        productTestsExecuted=0,coverage=None,externalActions=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
