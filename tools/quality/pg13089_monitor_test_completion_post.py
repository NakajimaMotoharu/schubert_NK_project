"""Independent original81 Program018 case/index/document binding, not another Product run."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13089-monitor-test-completion-post-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13088-monitor-test-completion-v1/manifest.json','5b06c9a07146b2bbcb0e828cbad3c3bc4dbeeec44fa636807d2aa7c192a18f1b')
    item = data.read_checked(data.ROOT/m['programIndex'],m['programIndexSha256'])
    proof = data.read_checked(data.BASE/'PG13082-monitor-test-post-v1/manifest.json','911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc')
    plan = data.read_checked(data.BASE/'PG13074-monitor-test-plan-v1/manifest.json','26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09')
    assert m['source'] == item['source'] == proof['source'] == plan['source'] == '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
    assert m['actualExit'] == item['actualExit'] == proof['actualExit'] == 0
    assert item['cases'] == plan['cases'] and item['observedOwnTests'] == 81 and item['suites'] == 10
    assert item['existingMethodIds'] == [r['className']+'#'+r['method'] for r in plan['cases']] and len(set(item['existingMethodIds'])) == 81
    assert m['newUniqueTestIds'] == item['newUniqueTestIds'] == 0 and not m['runDuplicated'] and m['productReruns'] == 0
    assert item['selectedMain'] == proof['selectedMain'] and item['monitorGroups'] == proof['monitorGroups']
    assert not item['selectedMainClosureCoverage100'] and all(r['coverage100'] for r in item['monitorGroups'].values())
    assert item['scopeRaw'] == 20 and item['staticGateExit'] == 1 and item['spotbugsSixExit'] == 0 and item['newAccepted'] == 0
    assert not item['wholeF03Accepted'] and not item['whole451Accepted'] and not item['formalUpdated']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in item['documentHashes'].items())
    assert all(data.sha((data.ROOT/r['path']).read_bytes()) == r['sourceSha256'] for r in item['cases'])
    directory = (data.ROOT/m['programIndex']).parent
    assert not directory.is_symlink() and [p.name for p in directory.iterdir()] == ['manifest.json']
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionManifestSha256='5b06c9a07146b2bbcb0e828cbad3c3bc4dbeeec44fa636807d2aa7c192a18f1b',
        programIndexSha256=m['programIndexSha256'],originalMethodBindings=81,newUniqueTestIds=0,
        sourceAndDocumentHashesMatched=True,scopeRaw=20,staticGateExit=1,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
