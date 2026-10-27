"""Current21 fixture fixes with20 existing thread source references rebound and10 retained unclassified."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11604_current_remaining_main_reason_delta_v2 import state as before_remaining_reasons
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11630-current-db-pool-binding-literal-delta-v1'
SOURCE='b2790ba78d8876c058dfcebf46e25805ac0bf56e'
CONTEXT_SHA='4cd805b22bfd8bac876ccf0f4a1ea3f6d3377f13fc95c80f94e17dad43a73eb4'

def state():
    ids,refs,pending=before_remaining_reasons()
    mp=data.BASE/'PG11604-current-remaining-main-reason-delta-v2/manifest.json'
    m=data.read_checked(mp,'32fc3e82b65c092166fa54ee9848d398cf5d832908823be129796170371f73ce')
    delta=data.read_checked(mp.parent/'delta.json',m['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(delta['removedFindingIds']))|set(delta['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,3070,511]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    old=data.read_checked(data.BASE/'PG11536-memory-http-guard-six-compile-v1/manifest.json','038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    current={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if old['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11618-db-pool-binding-literal-static-v1/manifest.json'
    static=data.read_checked(sp,'5a3585696589d6307496597bc5672bde35d35d71dddc2db09962b48c353bc334')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    cp=data.BASE/'PG11629-db-pool-binding-thread-context-v1';context=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',context['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==20 and context['source']==SOURCE and context['actualExit']==0
    fresh=[]
    for path,node in actual:
        assert path in changed and node.get('rule') in ('DoNotUseThreads','AvoidLiteralsInIfCondition','CloseResource')
        identity=original_match(path,node,original,actual)
        if identity['id'] in contexts:
            row=contexts[identity['id']]
            assert row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA if identity['id'] in contexts else None,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if identity['id'] in contexts else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh};scope={r['id'] for r in original if r['path'] in changed}&ids
    assert len(scope)==51 and len(fresh)==len(fresh_ids)==30 and fresh_ids<=scope
    assert scope&refs==set(contexts) and not scope&pending
    cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert [len(cr),len(cpending)]==[3070,531]
    removed=scope-fresh_ids
    assert len(removed)==21 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    current_ids=ids-removed
    assert len(current_ids)==8875 and len({r['id'] for r in original}-current_ids)==542 and len([i for i in current_ids if i.startswith('PMD-NEW-')])==8
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],
        originalScopeFindings=51,oldScopeFindings=51,newScopeFindings=30,replacedContextWarnings=20,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8896,sourceDerivedRaw=8875,
        mainRaw=1512,testRaw=7363,totalPriorCorrections=542,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=21,
        joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(current_ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
