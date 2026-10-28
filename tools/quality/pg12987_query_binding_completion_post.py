"""Independently validate new Program013 index, original failed save and current doc binding."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12987-query-binding-completion-post-v1'; assert not out.exists()
    m = data.read_checked(data.BASE/'PG12986-query-binding-completion-v2/manifest.json','74ccffd1a2ce659c0c50ec3880115513b3b9673f89733bf18e0f000a625f05c5')
    assert m['actualExit'] == 0 and m['observedProductTests'] == 6 and m['newBusinessTestIds'] == 4
    index = data.ROOT/m['programIndexPath']; p = data.read_checked(index,m['programIndexSha256'])
    assert index.parent.parent == data.ROOT/'evidence/01_PT/013_NK-NTF-001/evidence'
    assert all(not x.is_symlink() for x in [index,index.parent,index.parent.parent,index.parent.parent.parent])
    assert list(index.parent.iterdir()) == [index]
    assert p['source'] == m['source'] == '762568bb0338749c9549ec937cc2c79e84418836'
    assert p['actualExit'] == 0 and not p['fullProgramAccepted'] and p['newAccepted'] == 0
    assert p['observedProductTests'] == 6 and p['newUniqueTestIds'] == len(p['newTestIdMappings']) == 4
    assert [r['testId'] for r in p['newTestIdMappings']] == ['PT-QRY-BIND001','PT-QRY-BIND002','PT-QRY-BIND003','PT-QRY-BIND004']
    assert len({r['method'] for r in p['newTestIdMappings']}) == 4 and all(r['actual'] == 'PASS' for r in p['newTestIdMappings'])
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in m['documents'].items())
    failure = json.loads((data.BASE/'PG12984-query-binding-completion-v1/failure.safe.json').read_bytes())
    assert failure['actualExit'] == 1 and not failure['completionManifestCreated'] and not failure['programIndexCreated']
    assert data.sha((data.ROOT/failure['entry']).read_bytes()) == failure['entrySha256']
    prior_indexes = ['007_NK-AUT-001/evidence/pure-login-window-sequence','011_NK-QST-001/evidence/public-receipt-recovery']
    for name in prior_indexes:
        old = json.loads((data.ROOT/'evidence/01_PT'/name/'manifest.json').read_bytes())
        assert old['actualExit'] == 0 and old['source'] != m['source'] and old['newAccepted'] == 0
    verify(invocation); out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionSha256='74ccffd1a2ce659c0c50ec3880115513b3b9673f89733bf18e0f000a625f05c5',
        indexSha256=m['programIndexSha256'],originalFailurePreserved=True,existingSuccessfulProgramIndexesUnchangedReferences=prior_indexes,
        observedOriginalTests=6,additionalProductExecutions=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((out/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
