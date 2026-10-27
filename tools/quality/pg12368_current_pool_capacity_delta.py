"""Bind exact11 checksum/health Test corrections and two current worker contexts; retain all820 fixes/new8."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12338_current_remaining_main_maps_delta import state as before_maps
from pg11054_api_request_context import original_match

SOURCE='e2a04c5d5775b8629ce3c4f17259d8378b2bb5f9'
OUT=data.BASE/'PG12368-current-pool-capacity-delta-v1'
CONTEXT_SHA='f12539d10a80416aaebafc9210b2c3587801da0e6a0f21855b032d4e85a0bfec'

def state():
    ids,refs,pending=before_maps();p=data.BASE/'PG12338-current-remaining-main-maps-delta-v1/manifest.json';m=data.read_checked(p,'ac6daf60dbf666a1ed0af9b17a49c1ad651e963e7bc54a555ab7c7733521fdde');d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8583,3122,670]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG12352-pool-capacity-six-compile-v1/manifest.json','5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0');old=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==4 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG12356-pool-capacity-static-v1';static=data.read_checked(sp/'manifest.json','fce42d8b4757ef8be42f5d7d8f9436f5f5cf52928e1c4b9535fca984e5387b16');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG12359-pool-capacity-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==24 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']]
        assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==40 and len(fresh)==len(fresh_ids)==24 and set(contexts)==fresh_ids and len(removed)==16 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    assert len(scope&refs)==15 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    assert len(current)==8567 and len({r['id'] for r in original}-current)==850 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=40,oldScopeFindings=40,newScopeFindings=24,priorScopeCorrectionsRetained=0,replacedContextWarnings=15,newContextReferencesNet=9,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=8583,sourceDerivedRaw=8567,mainRaw=1512,testRaw=7055,totalPriorCorrections=850,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=16,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8567-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
