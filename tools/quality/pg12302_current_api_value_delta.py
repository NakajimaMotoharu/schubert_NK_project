"""Bind exact11 checksum/health Test corrections and two current worker contexts; retain all820 fixes/new8."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12264_current_bundle_maps_delta import state as before_maps
from pg11054_api_request_context import original_match

SOURCE='7368ba9d4a38677f5eade903771832e612aa42b5'
OUT=data.BASE/'PG12302-current-api-value-delta-v1'
CONTEXT_SHA='4d3f6cf82d1bb4d5a0a5a3a50afcfe3accea90fa446dd9fe634daf1e6f87abb1'

def state():
    ids,refs,pending=before_maps()
    p=data.BASE/'PG12264-current-bundle-maps-delta-v1/manifest.json'
    m=data.read_checked(p,'ff1aee075eb908f0b2cfff9994a9f3dd259761d61f1913c076d6d21875979167')
    d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8597,3114,660]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json','776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b');old=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==4 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12290-api-value-static-v1';static=data.read_checked(sp/'manifest.json','3d593e24fabfd7a5ec0323f9b308c47c1b2106dfa66dc16210c6a5f80e89954c');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12293-api-value-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==2 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']]
        assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==11 and len(fresh)==len(fresh_ids)==2 and set(contexts)==fresh_ids and len(removed)==9 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    assert len(scope&refs)==2 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert len(current)==8588 and len({r['id'] for r in original}-current)==829 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=11,oldScopeFindings=11,newScopeFindings=2,priorScopeCorrectionsRetained=0,replacedContextWarnings=2,newContextReferencesNet=0,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=8597,sourceDerivedRaw=8588,mainRaw=1512,testRaw=7076,totalPriorCorrections=829,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=9,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8588-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
