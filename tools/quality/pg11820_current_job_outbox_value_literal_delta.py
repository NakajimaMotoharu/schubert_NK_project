"""Bind10 actual duplicate fixes and12 current reasons; retain prior605 and all8 added diagnostics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11780_current_jdbc_collector_literal_delta import state as before_jdbc
from pg11054_api_request_context import original_match

SOURCE='60f62bd5dffb11e9943fc7578d9bddf380f8003c'
OUT=data.BASE/'PG11820-current-job-outbox-value-literal-delta-v1'
CONTEXT_SHA='cafc772777dea065b2c37ceeb582cda3418475ea2efed811bd28f21fcdca1eac'

def state():
    ids,refs,pending=before_jdbc();p=data.BASE/'PG11780-current-jdbc-collector-literal-delta-v1/manifest.json';m=data.read_checked(p,'37154957f609bd2a59fe16b9f6e413e10b88c964240a6c53dbf7fb5685a4320a');d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8812,3085,574]
    return ids,refs,pending

def inputs():
    ids,refs,pending=state();normal=data.read_checked(data.BASE/'PG11804-job-outbox-value-literal-six-compile-v1/manifest.json','cfa574ea833d73ee31adfb96fba25fb5909890a2fb1fe32413049618b4ca58ea');old=data.read_checked(data.BASE/'PG11764-jdbc-collector-literal-six-compile-v1/manifest.json','a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')};changed={p:h for p,h in java.items() if old['begin']['inputHashes'][p]!=h};assert len(java)==1810 and len(changed)==3 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11808-job-outbox-value-literal-static-v1';static=data.read_checked(sp/'manifest.json','c7d692599949d97030a84d4612b8110171dcaeb21d4786808de6180d7218f2af');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');cp=data.BASE/'PG11811-job-outbox-value-owner-context-v1';cm=data.read_checked(cp/'manifest.json',CONTEXT_SHA);review=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in review['rows']};assert len(contexts)==12 and cm['source']==SOURCE and cm['actualExit']==0
    fresh=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);row=contexts[identity['id']];assert path in changed and row['path']==path and row['attributes']==dict(node.attrib) and row['sourceSha256']==changed[path] and row['originalRowSha256']==identity['rowSha256']
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=CONTEXT_SHA,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope={r['id'] for r in original if r['path'] in changed}&ids;fresh_ids={r['id'] for r in fresh};removed=scope-fresh_ids
    assert len(scope)==22 and len(fresh)==len(fresh_ids)==12 and fresh_ids==set(contexts) and len(removed)==10 and all(r['rule'] in ('AvoidDuplicateLiterals',) for r in original if r['id'] in removed)
    assert len(scope&refs)==6 and scope&refs<=fresh_ids
    current=ids-removed;cr=(refs-scope)|fresh_ids;cpending=(pending-scope)|fresh_ids
    assert len(current)==8802 and len({r['id'] for r in original}-current)==615 and len([i for i in current if i.startswith('PMD-NEW-')])==8
    return changed,fresh,removed,cr,cpending,len(scope&pending)

def main():
    invocation=capture(__file__);assert not OUT.exists();changed,fresh,removed,refs,pending,oldpending=inputs();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=22,oldScopeFindings=22,newScopeFindings=12,priorScopeCorrectionsRetained=0,replacedContextWarnings=6,newContextReferencesNet=6,priorScopePending=oldpending,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=3,otherSourcePathsUnchanged=1807,originalRaw=9409,priorDerivedRaw=8812,sourceDerivedRaw=8802,mainRaw=1512,testRaw=7290,totalPriorCorrections=615,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=10,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=8802-len(refs),actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
