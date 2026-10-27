"""Remove eight measured GC literal warnings while retaining all six introduced diagnostic IDs."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11460_current_gc_fake_guard_delta import state as before_gc
import pg11481_api_web_gc_literal_context as context_stage

OUT=data.BASE/'PG11490-current-api-web-gc-literal-delta-v1'
SOURCE='d1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7'

def state():
    ids,refs,pending=before_gc()
    mp=data.BASE/'PG11460-current-gc-fake-guard-delta-v1/manifest.json'
    manifest=data.read_checked(mp,'3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2')
    delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(delta['removedFindingIds']))|set(delta['addedFindingIds'])
    refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8918,2787,228]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual,discoveries=context_stage.inputs()
    previous=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json','0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if previous['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    cp=data.BASE/'PG11481-api-web-gc-literal-context-v1/manifest.json'
    context=data.read_checked(cp,'06a16aa30c664c67ff9bf24005406af9ab3fc2dfd74097c58328a08ec54b6d14')
    rows=data.read_checked(cp.parent/'contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11483-api-web-gc-literal-context-post-v1/manifest.json','986e6fd56c232e602661eeaa714e69f7ed1f418b5a7668ae5769539985c28e6d')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows};fresh=[]
    for path,node in actual:
        assert path in changed
        identity=context_stage.identity(path,node,original,actual,discoveries)
        assert identity['id'] in reviewed
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),
            attributes=dict(node.attrib),identityRowSha256=identity['rowSha256'],origin=identity.get('origin','ORIGINAL_10690_DIAGNOSTIC'),
            contextManifestSha256='06a16aa30c664c67ff9bf24005406af9ab3fc2dfd74097c58328a08ec54b6d14',status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    discovered_scope={r['id'] for r in discoveries if r['path'] in changed}
    scope=(original_scope|discovered_scope)&ids
    assert len(original_scope)==28 and len(discovered_scope)==4 and len(scope)==32 and len(fresh_ids)==len(fresh)==24
    assert len(scope&refs)==len(scope&pending)==24 and discovered_scope<=fresh_ids
    removed=scope-fresh_ids
    assert len(removed)==8 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    cr,cpending=(refs-scope)|reviewed,(pending-scope)|reviewed
    current_ids=ids-removed
    assert len(current_ids)==8910 and len({r['id'] for r in original}-current_ids)==505 and {r['id'] for r in discoveries}<=current_ids
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],
        originalScopeFindings=28,previouslyIntroducedScopeFindingIds=sorted(discovered_scope),oldScopeFindings=32,newScopeFindings=24,
        preservedAllSixNewFindingIds=sorted(r['id'] for r in discoveries),replacedContextWarnings=24,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8918,sourceDerivedRaw=8910,
        mainRaw=1512,testRaw=7398,totalPriorCorrections=505,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=6,sourceScopeCorrectionsAlreadyCounted=8,
        joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(current_ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
    print(dict(raw=len(current_ids),refs=len(cr),pending=len(cpending),withoutReference=len(current_ids-cr)))

if __name__=='__main__':
    main()
