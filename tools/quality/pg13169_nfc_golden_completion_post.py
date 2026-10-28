"""Independent Program002 source/document/Test-ID binding, never re-execute Product cases."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13169-nfc-golden-completion-post-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13168-nfc-golden-completion-v1/manifest.json','4b22b6a4e2c61afb26c8942c5b51e12679a1cc7be9f7d0ba2a129ff495f37d73')
    item = data.read_checked(data.ROOT/m['programIndex'],m['programIndexSha256'])
    proof = data.read_checked(data.ROOT/item['proofManifest'],item['proofManifestSha256'])
    plan = data.read_checked(data.BASE/'PG13154-nfc-golden-plan-v1/manifest.json','7695d1297c842faf24096b623194ff74903b849d58f2b4355f002ae9b5a5748f')
    assert m['source'] == item['source'] == proof['source'] == plan['source'] == 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
    assert m['actualExit'] == item['actualExit'] == proof['actualExit'] == 0
    assert item['cases'] == plan['cases'] and item['observedOwnTests'] == proof['observedTestExecutions'] == 8 and item['suites'] == 2
    assert set(item['newTestIdBindings']) == {'PT-CODEC-NFCGOLD001','PT-CODEC-NFCGOLD002','PT-CODEC-NFCGOLD003'}
    assert len(item['existingRelatedMethodIds']) == 5 and len(set(item['existingRelatedMethodIds'])) == 5
    assert list(item['newTestIdBindings'].values()) == [r for r in plan['cases'] if r['path'].endswith('/FieldCodecNfcGoldenTest.java')]
    assert item['dimensions'] == proof['dimensions'] and item['selectedMain'] == proof['selectedMain'] and not item['selectedMainCoverage100']
    assert item['newUniqueTestIds'] == m['newUniqueTestIds'] == 3 and not item['oldExecUnion'] and m['productReruns'] == 0
    assert item['rawStatic'] == item['spotbugsSixExit'] == item['newAccepted'] == 0 and not item['whole451Accepted'] and not item['formalUpdated'] and item['effortPercent'] is None
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in item['documentHashes'].items())
    assert all(data.sha((data.ROOT/row['path']).read_bytes()) == row['sourceSha256'] for row in item['cases'])
    assert data.sha((data.ROOT/'tools/quality/pg13162_nfc_golden_post.py').read_bytes()) == '21dfde905eacf180730e2a8233175e818cd49dc5e6923bc6183e4692260a4b75'
    directory = (data.ROOT/m['programIndex']).parent;assert not directory.is_symlink() and [p.name for p in directory.iterdir()] == ['manifest.json']
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionManifestSha256='4b22b6a4e2c61afb26c8942c5b51e12679a1cc7be9f7d0ba2a129ff495f37d73',programIndexSha256=m['programIndexSha256'],
        newUniqueTestIds=3,existingRelatedMethodIds=5,sourceDocumentAndFailedEntryHashesMatched=True,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
