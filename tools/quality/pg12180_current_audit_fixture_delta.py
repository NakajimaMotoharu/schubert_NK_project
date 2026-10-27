"""Bind12 Batch pure value fixes and1 current loader reference; retain prior775 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12150_current_batch_value_fixture_delta import state as before_jms
from pg11054_api_request_context import original_match

SOURCE='92c80a593717465426a33bdf581bc7e94b1235f1'
OUT=data.BASE/'PG12180-current-audit-fixture-delta-v1'
CONTEXT_SHA='6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e'

def state():
    ids,refs,pending=before_jms();p=data.BASE/'PG12150-current-batch-value-fixture-delta-v1/manifest.json';m=data.read_checked(p,'9a82e11f706c25da0a06835d8d1fe3e8a805df4b5ee676e303fb852016ab928a');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8630,3102,642]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json','462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048');old=data.read_checked(data.BASE/'PG12134-batch-value-fixture-six-compile-v1/manifest.json','6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12168-audit-fixture-static-v1';static=data.read_checked(sp/'manifest.json','7782fd394e8f7972e0dfc878264791ce2f6540da31574f8a0eb7dfbdc0840845');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12175-audit-fixture-context-v2';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==3 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts.get(identity['id']);assert path in changed
        if row:
            assert row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        else:assert node.get('rule') in ('AvoidFieldNameMatchingMethodName','AvoidLiteralsInIfCondition')
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA if row else None,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if row else 'APPLICABILITY_PENDING_UNFIXED_FIELD_OR_IF',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==18 and len(fresh)==len(fresh_ids)==5 and set(contexts)<fresh_ids and len(removed)==13 and all(r['rule'] in ('AvoidDuplicateLiterals',) for r in original if r['id'] in removed)
    assert len(scope&refs)==2 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert len(current)==8617 and len({r['id'] for r in original}-current)==800 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=18,oldScopeFindings=18,newScopeFindings=5,priorScopeCorrectionsRetained=0,replacedContextWarnings=2,newContextReferencesNet=1,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8630,sourceDerivedRaw=8617,mainRaw=1512,testRaw=7105,totalPriorCorrections=800,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=13,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8617-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
