"""Current raw-ID join including six genuinely new diagnostics; no analyzer or product replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11428_current_api_web_payload_literal_delta import state as before_payload
import pg11451_gc_fake_guard_context_v3 as context_stage

OUT=data.BASE/'PG11460-current-gc-fake-guard-delta-v1'
SOURCE='495313cd8e724d5f1906fca64d9d9fd3516aae50'

def state():
    ids,refs,pending=before_payload()
    p=data.BASE/'PG11428-current-api-web-payload-literal-delta-v1/manifest.json'
    manifest=data.read_checked(p,'634c62599b0b66df92dd63a7038298153ff4201c10feb41d3925b304be5cd78d')
    delta=data.read_checked(p.parent/'delta.json',manifest['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids-=set(delta['removedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8912,2757,194]
    return ids,refs,pending

def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=context_stage.inputs()
    previous=data.read_checked(data.BASE/'PG11412-api-web-payload-literal-six-compile-v1/manifest.json','b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if previous['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    cp=data.BASE/'PG11451-gc-fake-guard-context-v3/manifest.json'
    context=data.read_checked(cp,'6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb')
    rows=data.read_checked(cp.parent/'contexts.json',context['contextsSha256'])
    new=data.read_checked(cp.parent/'new-diagnostics.json',context['newDiagnosticsSha256'])
    post=data.read_checked(data.BASE/'PG11453-gc-fake-guard-context-post-v3/manifest.json','ab7430e60bc819fbe2d938d077999ad886e274ee449787e28e73441d3b88d0e7')
    assert post['actualExit']==0 and post['source']==SOURCE and new==context_stage.discoveries(actual,normal['begin']['inputHashes'])
    reviewed={r['id'] for r in rows};new_ids={r['id'] for r in new}
    assert len(new_ids)==6 and not new_ids&ids
    fresh=[]
    for path,node in actual:
        assert path in changed
        identity=context_stage.identity(path,node,original,actual,new)
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),
            attributes=dict(node.attrib),identityRowSha256=identity['rowSha256'],origin=identity.get('origin','ORIGINAL_10690_DIAGNOSTIC'),
            contextManifestSha256='6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb' if identity['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if identity['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    old_scope=original_scope&ids
    assert len(old_scope)==38 and len(fresh)==len(fresh_ids)==44 and fresh_ids==old_scope|new_ids
    assert len(reviewed)==36 and reviewed|set(context['unclassifiedOriginalIds'])==fresh_ids
    removed=old_scope-fresh_ids
    assert not removed
    current_ids=ids|new_ids
    cr,cpending=(refs-old_scope)|reviewed,(pending-old_scope)|reviewed
    assert len(current_ids)==8918 and len(original)==9409 and len({r['id'] for r in original}-current_ids)==497
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=[],addedFindingIds=sorted(new_ids),
        newDiagnosticRegistryPath=str((cp.parent/'new-diagnostics.json').relative_to(data.ROOT)),newDiagnosticRegistrySha256=context['newDiagnosticsSha256'],
        originalScopeFindings=len(original_scope),previouslyRemovedIds=sorted(original_scope-old_scope),oldScopeFindings=38,newScopeFindings=44,
        replacedContextWarnings=len(old_scope&refs),newContextReferencesNet=len(cr)-len(refs),newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=8912,sourceDerivedRaw=8918,
        mainRaw=1512,testRaw=7406,totalPriorCorrections=497,newDiagnosticsAdded=6,sourceScopeCorrectionsAlreadyCounted=0,
        joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(current_ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
    print(dict(raw=len(current_ids),refs=len(cr),pending=len(cpending),withoutReference=len(current_ids-cr),oldScope=len(old_scope),oldReferenced=len(old_scope&refs)))

if __name__=='__main__':
    main()
