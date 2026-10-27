"""Current8 fatal comparison fixes,20 thread references rebound and two new bounded owner references."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11630_current_db_pool_binding_literal_delta import state as before_pool_literals
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11660-current-db-pool-binding-fatal-case-delta-v1'
SOURCE='b4810698856cc2ae7edabb899a47aad34ef52cc2'
CONTEXT_SHA='581e4415fdddde304b466767d4cebed8a249dd7c82f3a41158b804a5b1df316b'

def state():
    ids,refs,pending=before_pool_literals()
    mp=data.BASE/'PG11630-current-db-pool-binding-literal-delta-v1/manifest.json'
    m=data.read_checked(mp,'7ed13627439a06052d80f43aca4e74b32d759ecc2daebbfdfe495d1b476829c9')
    delta=data.read_checked(mp.parent/'delta.json',m['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(delta['removedFindingIds']))|set(delta['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8875,3070,531]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG11644-db-pool-binding-fatal-case-six-compile-v1/manifest.json','b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6')
    old=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    current={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if old['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11648-db-pool-binding-fatal-case-static-v1/manifest.json'
    static=data.read_checked(sp,'acead561d795d044cc51826684268d6b2729f529fd86bd2bfa21688e887869c2')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    cp=data.BASE/'PG11651-db-pool-binding-current-owner-context-v1';context=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',context['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==22 and context['source']==SOURCE and context['actualExit']==0
    fresh=[]
    for path,node in actual:
        assert path in changed and node.get('rule') in ('DoNotUseThreads','CloseResource')
        identity=original_match(path,node,original,actual)
        if identity['id'] in contexts:
            row=contexts[identity['id']]
            assert row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA if identity['id'] in contexts else None,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if identity['id'] in contexts else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh};scope={r['id'] for r in original if r['path'] in changed}&ids
    assert len(scope)==30 and len(fresh)==len(fresh_ids)==22 and fresh_ids<=scope
    assert len(scope&refs)==20 and scope&refs<=set(contexts) and scope&pending==scope&refs
    cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert [len(cr),len(cpending)]==[3072,533]
    removed=scope-fresh_ids
    assert len(removed)==8 and all(r['rule']=='AvoidLiteralsInIfCondition' for r in original if r['id'] in removed)
    current_ids=ids-removed
    assert len(current_ids)==8867 and len({r['id'] for r in original}-current_ids)==550 and len([i for i in current_ids if i.startswith('PMD-NEW-')])==8
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],
        originalScopeFindings=51,oldScopeFindings=30,newScopeFindings=22,priorScopeCorrectionsRetained=21,replacedContextWarnings=20,newContextReferencesNet=2,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8875,sourceDerivedRaw=8867,
        mainRaw=1512,testRaw=7355,totalPriorCorrections=550,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=8,
        joinedContextWarnings=len(cr),sourceReboundCurrentWholePending=len(cpending),noCurrentReferenceInThisJoin=len(current_ids-cr),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
