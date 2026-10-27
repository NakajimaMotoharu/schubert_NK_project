"""Bind7 duplicate/if fixes and2 current reasons; retain prior638 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11880_current_web_exporter_fixture_delta import state as before_exporters
from pg11054_api_request_context import original_match

SOURCE='264dc69591876147d76c19082cb69658cfe03dd8'
OUT=data.BASE/'PG11910-current-session-json-fixture-delta-v1'
CONTEXT_SHA='bed3fc58d5eb27a5c30ca955caa7617f50bf36d3710b5fad401f76f7c92140da'

def state():
    ids,refs,pending=before_exporters();p=data.BASE/'PG11880-current-web-exporter-fixture-delta-v1/manifest.json';m=data.read_checked(p,'b72c0cd9d6b7a16a261742b9e5403bcf7b3f9c027b1ee264998c9a9f9324fdd6');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8779,3091,606]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json','3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0');old=data.read_checked(data.BASE/'PG11864-web-exporter-fixture-six-compile-v1/manifest.json','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11898-session-json-fixture-static-v1';static=data.read_checked(sp/'manifest.json','edf4a68b01e404ff0b728a50b8520e1d0fdbdf40417333f61519e241ecfec488');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG11901-session-json-owner-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==2 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==9 and len(fresh)==len(fresh_ids)==2 and fresh_ids==set(contexts) and len(removed)==7 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    assert len(scope&refs)==2 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8772 and len({r['id'] for r in original}-current)==645 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=9,oldScopeFindings=9,newScopeFindings=2,priorScopeCorrectionsRetained=0,replacedContextWarnings=2,newContextReferencesNet=0,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8779,sourceDerivedRaw=8772,mainRaw=1512,testRaw=7260,totalPriorCorrections=645,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=7,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8772-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
