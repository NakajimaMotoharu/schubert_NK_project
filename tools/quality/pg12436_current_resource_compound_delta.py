"""Source-only46 retained reasons: no code changes, no raw removals, no runtime credit."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12424_current_batch_runtime_delta import state as before_runtime

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
OUT = data.BASE/'PG12436-current-resource-compound-delta-v1'
CONTEXT = '20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de'

def state():
    ids,refs,pending = before_runtime()
    p = data.BASE/'PG12424-current-batch-runtime-delta-v1/manifest.json'
    m = data.read_checked(p,'466a2d8c537975bfee8de7c83633f38ce33dffb319c9fd326f82d8e248362268')
    d = data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    assert not d['freshRows'] and not d['addedFindingIds']
    ids -= set(d['removedFindingIds'])
    assert [len(ids),len(refs),len(pending)] == [8553,3135,720]
    return ids,refs,pending

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = state()
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    cp = data.BASE/'PG12432-resource-compound-context-v1';context = data.read_checked(cp/'manifest.json',CONTEXT)
    post = data.read_checked(data.BASE/'PG12434-resource-compound-context-post-v1/manifest.json','7457fb8e17f085e7022cca8aad1953eb61c5f3ae128d137cde2be6ba03f30ce3')
    assert context['source'] == post['source'] == SOURCE and context['actualExit'] == post['actualExit'] == 0
    review = data.read_checked(cp/'review.json',context['reviewSha256'])['rows']
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');lookup = {r['id']:r for r in original}
    fresh = []
    for r in review:
        old = lookup[r['id']]
        assert r['id'] in ids and r['id'] not in refs|pending and r['sourceSha256'] == hashes[r['path']] == old['inputSha256']
        assert r['attributes'] == old['attributes'] and r['originalRowSha256'] == old['rowSha256'] and '/src/main/java/' in r['path']
        fresh.append(dict(id=r['id'],path=r['path'],source=SOURCE,sourceKind='MAIN',currentInputSha256=r['sourceSha256'],rule=r['rule'],attributes=r['attributes'],originalRowSha256=r['originalRowSha256'],contextManifestSha256=CONTEXT,status='SOURCE_ONLY_CONTEXT_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    reviewed = {r['id'] for r in fresh};assert len(fresh) == len(reviewed) == context['sourceContexts'] == context['rawRetained'] == 46
    refs |= reviewed;pending |= reviewed
    assert [len(ids),len(refs),len(pending)] == [8553,3181,766]
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta={},freshRows=fresh,removedFindingIds=[],addedFindingIds=[],selectedRetainedRaw=46,originalTwoSourceRaw=48,replacedContextWarnings=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=0,sourceDerivedRaw=8553,mainRaw=1512,testRaw=7041,totalPriorCorrections=864,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,sourceContexts=46,rawRetained=46,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,wholeCurrentAnalyzerReissued=False,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
