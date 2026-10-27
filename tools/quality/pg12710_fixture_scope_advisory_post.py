"""Independent fixed original owner and simple explicit source import result checks; no Product run."""
import copy
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e353b1f49a740a426031fdc199f7ce8b26081971'
OUT = data.BASE/'PG12710-fixture-scope-advisory-post-v1'
PROOF = 'ac333e9ff10297a7a93eb60523bd5b9ac786080e53a07fa67b0042a5ce4f4082'
WRITER = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/ScenarioRecordStreamTest.java'
VERIFIER = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/TransferContentVerifierTest.java'
OWNERS = [dict(path=WRITER, canonicalOwner='WBS-P008-06', canonicalCostOwner='WBS-P008-06'), dict(path=VERIFIER, canonicalOwner='WBS-P008-03', canonicalCostOwner='WBS-P008-03')]


def require(value):
    if not (value['actualExit']==0 and value['source']==SOURCE and value['metadataConsistent'] is True and value['metadataIssues']==[] and value['reviewedMainCount']==57 and value['explicitTextCount']==59 and len(value['inputHashes'])==59):
        raise ValueError('exact source and metadata-only scope required')
    if value['originalOwners'] != OWNERS:
        raise ValueError('independent exact original owner oracle required')
    if not (value['executionQualified'] is False and value['holdReleased'] is False and value['productTestsExecuted']==0 and value['newAccepted']==0 and value['coverage'] is None and len(value['limitations'])==4):
        raise ValueError('no execution qualification, acceptance or coverage transfer')
    if value['selftest']['positiveVectors'] != 3 or value['selftest']['negativeVectors'] != 24:
        raise ValueError('fixed metadata vectors required')
    kinds = {r['kind'] for r in value['priorDefectAdvisoryIssues']}
    if kinds != {'DIRECT_IMPORT_NOT_REVIEWED','EXPECTED_OWNER_DIFFERS_FROM_ORIGINAL'}:
        raise ValueError('both original metadata failure cases must be detected')


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    value = data.read_checked(data.BASE/'PG12708-fixture-scope-advisory-v1/manifest.json', PROOF)
    require(value)
    normal = data.read_checked(data.BASE/'PG12686-scenario-writer-six-compile-v1/manifest.json', value['normalManifestSha256'])
    registry = data.read_checked(data.BASE/'PG12700-scenario-writer-trace-v2/manifest.json', value['registryManifestSha256'])
    assert normal['source'] == registry['source'] == SOURCE and normal['actualExit'] == registry['actualExit'] == 0
    known = {p.split('/java/',1)[1][:-5].replace('/','.') : p for p in value['inputHashes'] if '/src/main/' in p}
    assert len(known) == 57
    imports = {}
    for path, digest in value['inputHashes'].items():
        assert path.startswith('src/schubert-nk-') and path.endswith('.java') and '/java/dev/codex/schubert/nk/' in path and '..' not in path.split('/')
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == digest == normal['begin']['inputHashes'][path]
        names = re.findall(r'^import (dev\.codex\.schubert\.nk\.[\w.]+);$', text, re.M)
        assert not re.findall(r'^import static dev\.codex\.schubert\.nk\.', text, re.M)
        assert set(names) <= set(known)
        imports[path] = [dict(name=name,static=False,outerSourceCandidate=known[name]) for name in names]
    assert value['directImports'] == imports
    original = {row['path']:row for row in registry['sourceRows']}
    assert len(original) == len(registry['sourceRows']) == 983
    for owner in OWNERS:
        row = original[owner['path']]
        assert row['sha256'] == value['inputHashes'][owner['path']]
        assert all(row[key] == owner[key] for key in ['canonicalOwner','canonicalCostOwner'])
    labels = []
    for field, bad_value in [('source','0'*40), ('metadataConsistent',False), ('executionQualified',True), ('holdReleased',True), ('productTestsExecuted',8), ('newAccepted',1), ('coverage',100), ('originalOwners',list(reversed(OWNERS)))]:
        bad = copy.deepcopy(value)
        assert bad[field] != bad_value
        bad[field] = bad_value
        try:
            require(bad)
        except ValueError:
            labels.append(field)
        else:
            raise AssertionError('metadata promotion or wrong owner accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,proofManifestSha256=PROOF,independentOriginalOwners=OWNERS,explicitInputHashes=value['inputHashes'],independentImportRows=sum(map(len, imports.values())),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,toolPositiveVectors=3,toolNegativeVectors=24,executionQualified=False,holdReleased=False,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
