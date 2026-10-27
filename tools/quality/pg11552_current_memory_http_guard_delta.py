"""Join two newly observed memory cleanup diagnostics without dropping original52 or earlier new6."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11520_current_metric_http_literal_delta import state as before_literals
import pg11543_memory_http_guard_context as context_stage

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11552-current-memory-http-guard-delta-v1'

def state():
    ids,refs,pending=before_literals()
    mp=data.BASE/'PG11520-current-metric-http-literal-delta-v1/manifest.json'
    m=data.read_checked(mp,'e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab')
    delta=data.read_checked(mp.parent/'delta.json',m['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids-=set(delta['removedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8894,2787,228]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=state();normal,original,actual=context_stage.inputs()
    previous=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if previous['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    cp=data.BASE/'PG11543-memory-http-guard-context-v1/manifest.json'
    context=data.read_checked(cp,'db8f662a118b6e798b982992cc70c6819366156e5c5974f79bd91238071680b6')
    rows=data.read_checked(cp.parent/'contexts.json',context['contextsSha256']);new=data.read_checked(cp.parent/'new-diagnostics.json',context['newDiagnosticsSha256'])
    post=data.read_checked(data.BASE/'PG11545-memory-http-guard-context-post-v1/manifest.json','8707d944c0306c9dbc20b62556630613d109697618adf7c20c9b753874c04653')
    assert post['actualExit']==0 and post['source']==SOURCE and new==context_stage.discoveries(actual,normal['begin']['inputHashes'])
    reviewed={r['id'] for r in rows};new_ids={r['id'] for r in new};assert len(new_ids)==2 and not new_ids&ids
    fresh=[]
    for path,node in actual:
        assert path in changed;identity=context_stage.identity(path,node,original,actual,new)
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),
            identityRowSha256=identity['rowSha256'],origin=identity.get('origin','ORIGINAL_10690_DIAGNOSTIC'),contextManifestSha256='db8f662a118b6e798b982992cc70c6819366156e5c5974f79bd91238071680b6',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    original_scope={r['id'] for r in original if r['path'] in changed};old_scope=original_scope&ids;fresh_ids={r['id'] for r in fresh}
    assert len(original_scope)==68 and len(old_scope)==52 and len(fresh)==len(fresh_ids)==54 and fresh_ids==old_scope|new_ids==reviewed
    assert not old_scope&refs and not old_scope&pending
    current_ids=ids|new_ids;cr=(refs-old_scope)|reviewed;cpending=(pending-old_scope)|reviewed
    assert len(current_ids)==8896 and len({r['id'] for r in original}-current_ids)==521 and len([i for i in current_ids if i.startswith('PMD-NEW-')])==8
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=[],addedFindingIds=sorted(new_ids),
        newDiagnosticRegistryPath=str((cp.parent/'new-diagnostics.json').relative_to(data.ROOT)),newDiagnosticRegistrySha256=context['newDiagnosticsSha256'],
        originalScopeFindings=68,previouslyRemovedIds=sorted(original_scope-old_scope),oldScopeFindings=52,newScopeFindings=54,replacedContextWarnings=0,newContextReferencesNet=54,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,
        originalRaw=9409,priorDerivedRaw=8894,sourceDerivedRaw=8896,mainRaw=1512,testRaw=7384,totalPriorCorrections=521,newDiagnosticsAdded=2,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,
        joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(current_ids-cr),actualViolationCount=None,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
    print(dict(raw=len(current_ids),refs=len(cr),pending=len(cpending),withoutReference=len(current_ids-cr)))

if __name__=='__main__':
    main()
