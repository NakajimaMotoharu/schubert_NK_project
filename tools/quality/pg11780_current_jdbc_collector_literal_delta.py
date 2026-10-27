"""Bind14 actual fixes and12 current reasons, retaining prior591 corrections and all8 new diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11750_current_mq_recorder_literal_delta import state as before_mq
from pg11054_api_request_context import original_match

SOURCE='21daf2722f9b280ec005b1b971300774a1d3716f'
OUT=data.BASE/'PG11780-current-jdbc-collector-literal-delta-v1'
CONTEXT_SHA='64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1'

def state():
    ids,refs,pending=before_mq();p=data.BASE/'PG11750-current-mq-recorder-literal-delta-v1/manifest.json';m=data.read_checked(p,'687847fc012bb9850865b0570ab427c1df3e687626a53a75bb774e813f2287f2');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8826,3085,562]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG11764-jdbc-collector-literal-six-compile-v1/manifest.json','a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0');old=data.read_checked(data.BASE/'PG11734-mq-recorder-literal-six-compile-v1/manifest.json','7d0f5f532b32896695e553c7ae886cdfef02595cbeb3c54c85c78b95b541505b')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11768-jdbc-collector-literal-static-v1';static=data.read_checked(sp/'manifest.json','1fb16cae2dcaf613917f2a8bd4abce746130911ecf3525ab45b66c00748b3c68');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG11771-jdbc-collector-owner-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==12 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==26 and len(fresh)==len(fresh_ids)==12 and fresh_ids==set(contexts) and len(removed)==14 and all(r['rule'] in ('AvoidDuplicateLiterals','AssignmentInOperand') for r in original if r['id'] in removed)
    assert len(scope&refs)==12 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8812 and len({r['id'] for r in original}-current)==605 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=26,oldScopeFindings=26,newScopeFindings=12,priorScopeCorrectionsRetained=0,replacedContextWarnings=12,newContextReferencesNet=0,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8826,sourceDerivedRaw=8812,mainRaw=1512,testRaw=7300,totalPriorCorrections=605,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=14,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8812-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
