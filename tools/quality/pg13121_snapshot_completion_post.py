"""Independent Program008 case/source/document binding, without PT replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13121-snapshot-completion-post-v1'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13120-snapshot-completion-v1/manifest.json','9fbd1b232a174b7b8080d7e24511d0c9c1367d12c6ed9f12bd0eab0492343804')
    item = data.read_checked(data.ROOT/m['programIndex'],m['programIndexSha256'])
    proof = data.read_checked(data.BASE/'PG13112-snapshot-corrected-post-v1/manifest.json','2e506ef62e654842ad448b38aa0a61f90b26ebaa98e3b84f42df50d221f07c9d')
    plan = data.read_checked(data.BASE/'PG13104-snapshot-corrected-plan-v1/manifest.json','03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8')
    assert m['source'] == item['source'] == proof['source'] == plan['source'] == '5c378e064f0f8a7366316d4afa28fbb2cd9cec81'
    assert m['actualExit'] == item['actualExit'] == proof['actualExit'] == 0
    assert item['cases'] == plan['cases'] and len(item['cases']) == item['observedOwnTests'] == proof['newTestIds'] == 3 and item['suites'] == 1
    assert item['testIds'] == ['PT-SCN-SNAPSHOTMAX-001','PT-SCN-SNAPSHOTMAX-002','PT-SCN-SNAPSHOTMAX-003']
    assert item['selectedMain'] == proof['selectedMain'] and not item['selectedMainCoverage100'] and not item['wholeArtifactCoverage100']
    assert item['newAccepted'] == 0 and not item['whole451Accepted'] and not item['formalUpdated'] and item['effortPercent'] is None
    assert item['oldCandidateExit'] == 1 and not item['oldCandidateSuccessTransferred'] and item['additionalSourceQualificationCycles'] == 1
    assert m['productReruns'] == 0 and m['newUniqueTestIds'] == item['newUniqueTestIds'] == 3
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in item['documentHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in item['failedEntries'].items())
    assert all(data.sha((data.ROOT/r['path']).read_bytes()) == r['sourceSha256'] for r in item['cases'])
    for pin in item['inputPins'].values():
        assert data.read_checked(data.ROOT/pin['path'],pin['sha256'])['source'] == m['source']
    directory = (data.ROOT/m['programIndex']).parent
    assert not directory.is_symlink() and [p.name for p in directory.iterdir()] == ['manifest.json']
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionManifestSha256='9fbd1b232a174b7b8080d7e24511d0c9c1367d12c6ed9f12bd0eab0492343804',
        programIndexSha256=m['programIndexSha256'],newUniqueTestIds=3,sourceDocumentAndFailedEntryHashesMatched=True,
        productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
