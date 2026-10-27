"""Bind33 mode/duplicate/bound fixes and1 current reason; retain prior645 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11910_current_session_json_fixture_delta import state as before_session
from pg11054_api_request_context import original_match

SOURCE='fd113e37b0783ae86d50696c9d3844e80b258d8a'
OUT=data.BASE/'PG11940-current-storage-attribute-fixture-delta-v1'
CONTEXT_SHA='953bad12f2072ba6ae09f3462526b080dd06c6064dda06df73e3670ae17a462b'

def state():
    ids,refs,pending=before_session();p=data.BASE/'PG11910-current-session-json-fixture-delta-v1/manifest.json';m=data.read_checked(p,'6758bab7f719df7b3faa8c9f9636726d8ac7b2a504572c37d66eade0e5d6ff30');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8772,3091,608]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG11924-storage-attribute-fixture-six-compile-v1/manifest.json','6c9f579aa08c720ce523423efa8ca7dc64a941dac559a548927259f09f28555c');old=data.read_checked(data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json','3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11928-storage-attribute-fixture-static-v1';static=data.read_checked(sp/'manifest.json','1518ae6f87ba5342038fb964354e8f0ab34525ba2e76af5fabbb88a969f4933d');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG11931-storage-attribute-map-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==1 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==34 and len(fresh)==len(fresh_ids)==1 and fresh_ids==set(contexts) and len(removed)==33 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition','AvoidUsingOctalValues') for r in original if r['id'] in removed)
    assert len(scope&refs)==0 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8739 and len({r['id'] for r in original}-current)==678 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=34,oldScopeFindings=34,newScopeFindings=1,priorScopeCorrectionsRetained=0,replacedContextWarnings=0,newContextReferencesNet=1,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8772,sourceDerivedRaw=8739,mainRaw=1512,testRaw=7227,totalPriorCorrections=678,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=33,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8739-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
