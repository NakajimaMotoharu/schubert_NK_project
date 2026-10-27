"""Independent saved history + exact46 source-only overlay; no Product run or raw correction."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_saved_history_12424 import historical_to_12424

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
PIN = 'dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0'
CONTEXT = '20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de'
OUT = data.BASE/'PG12438-current-resource-compound-delta-post-v1'

def require(value,expected):
    if any(value.get(k) != v for k,v in expected.items()):
        raise ValueError('exact source-only46 overlay, no removal/runtime/formal credit required')

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = historical_to_12424()
    p = data.BASE/'PG12436-current-resource-compound-delta-v1';m = data.read_checked(p/'manifest.json',PIN)
    delta = data.read_checked(p/'delta.json',m['deltaSha256'])
    assert not delta['removedFindingIds'] and not delta['addedFindingIds'] and not delta['sourceInputDelta']
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0 and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    cp = data.BASE/'PG12432-resource-compound-context-v1';cm = data.read_checked(cp/'manifest.json',CONTEXT)
    contexts = {r['id']:r for r in data.read_checked(cp/'review.json',cm['reviewSha256'])['rows']}
    context_post = data.read_checked(data.BASE/'PG12434-resource-compound-context-post-v1/manifest.json','7457fb8e17f085e7022cca8aad1953eb61c5f3ae128d137cde2be6ba03f30ce3')
    assert cm['source'] == context_post['source'] == SOURCE and context_post['actualExit'] == 0 and context_post['metadataNegativeVectors'] == 25
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');lookup = {r['id']:r for r in original}
    paths = {'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScope.java'}
    selected = {r['id'] for r in original if r['path'] in paths and r['rule'] in ('AvoidCatchingGenericException','AvoidInstanceofChecksInCatchClause')}
    assert selected == set(contexts) == {r['id'] for r in delta['freshRows']} and len(delta['freshRows']) == 46 and selected <= ids and not selected & (refs|pending)
    for row in delta['freshRows']:
        old = lookup[row['id']];reason = contexts[row['id']];path = old['path']
        expected = dict(id=old['id'],path=path,source=SOURCE,sourceKind='MAIN',currentInputSha256=normal['begin']['inputHashes'][path],rule=old['rule'],attributes=old['attributes'],originalRowSha256=old['rowSha256'],contextManifestSha256=CONTEXT,status='SOURCE_ONLY_CONTEXT_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False)
        require(row,expected)
        assert row['currentInputSha256'] == old['inputSha256'] == reason['sourceSha256'] and reason['dynamicPtStatus'] == 'NOT_EXECUTED'
    refs |= selected;pending |= selected
    assert [len(ids),len(refs),len(pending)] == [8553,3181,766] and len({r['id'] for r in original}-ids) == 864 and len([i for i in ids if i.startswith('PMD-NEW-')]) == 8
    expected = dict(actualExit=0,source=SOURCE,changedSourcePaths=0,sourceDerivedRaw=8553,totalPriorCorrections=864,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,sourceContexts=46,rawRetained=46,joinedContextWarnings=3181,sourceReboundCurrentWholePending=766,actualViolationCount=None,wholeF03Accepted=False,newAccepted=0,productTestsExecuted=0)
    require(m,expected);negatives = 0
    for key,wrong in [('source','0'*40),('sourceDerivedRaw',8507),('totalPriorCorrections',910),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3135),('sourceReboundCurrentWholePending',720),('actualViolationCount',0),('wholeF03Accepted',True)]:
        assert expected[key] != wrong;bad = dict(m);bad[key] = wrong
        try:
            require(bad,expected)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('invalid source-only overlay cardinality accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=864,allIntroducedDiagnosticsRetained=8,sourceContexts=46,rawRetained=46,metadataNegativeVectors=negatives,sourceCorrections=0,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
