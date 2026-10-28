"""Independent nine-case Program002 binding; preserve old NFC index and source domain."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13187-numeric-ceiling-completion-post-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13186-numeric-ceiling-completion-v1/manifest.json','a04dedd403ed28763ae96860b77eb2968b653306e353e16bd83611780076e373')
    item = data.read_checked(data.ROOT/m['programIndex'],m['programIndexSha256'])
    proof = data.read_checked(data.ROOT/item['proofManifest'],item['proofManifestSha256'])
    plan = data.read_checked(data.BASE/'PG13174-numeric-ceiling-plan-v1/manifest.json','7cb6dbf4fb9b2532cd9e170dc18a71fcb6732a04314c693dc812ffea66c2a40d')
    assert m['source'] == item['source'] == proof['source'] == plan['source'] == '80ba5f783432c84b6facd83bcd3a80774f4e4665'
    assert m['actualExit'] == item['actualExit'] == proof['actualExit'] == 0 and item['cases'] == plan['cases']
    assert item['observedOwnTests'] == proof['observedTestExecutions'] == 9 and item['suites'] == 2
    assert list(item['newTestIdBindings']) == ['PT-CODEC-NUMMAX001'] and item['newTestIdBindings']['PT-CODEC-NUMMAX001']['method'] == 'numericSemanticCeilingIsIndependentOfWireAndLongCapacity'
    assert len(item['existingRelatedMethodIds']) == len(set(item['existingRelatedMethodIds'])) == 8
    assert item['dimensions'] == proof['dimensions'] and item['selectedMain'] == proof['selectedMain'] and item['selectedMainCoverage100'] is True
    assert item['newUniqueTestIds'] == m['newUniqueTestIds'] == 1 and not item['oldExecUnion'] and m['productReruns'] == 0
    assert item['rawStatic'] == item['spotbugsSixExit'] == item['newAccepted'] == 0 and not item['whole451Accepted'] and not item['formalUpdated'] and item['effortPercent'] is None
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in item['documentHashes'].items())
    assert all(data.sha((data.ROOT/row['path']).read_bytes()) == row['sourceSha256'] for row in item['cases'])
    directory = (data.ROOT/m['programIndex']).parent;assert not directory.is_symlink() and [p.name for p in directory.iterdir()] == ['manifest.json']
    old = data.read_checked(data.BASE/'PG13168-nfc-golden-completion-v1/manifest.json','4b22b6a4e2c61afb26c8942c5b51e12679a1cc7be9f7d0ba2a129ff495f37d73')
    data.read_checked(data.ROOT/old['programIndex'],old['programIndexSha256'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionManifestSha256='a04dedd403ed28763ae96860b77eb2968b653306e353e16bd83611780076e373',programIndexSha256=m['programIndexSha256'],
        newUniqueTestIds=1,existingRelatedMethodIds=8,sourceAndDocumentHashesMatched=True,oldNfcProgramIndexUnchanged=True,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
