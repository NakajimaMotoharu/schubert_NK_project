"""Current raw-ID binding of sixteen measured HTTP fixture fixes; retained52 stay unclassified."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11490_current_api_web_gc_literal_delta import state as before_gc_literals
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11520-current-metric-http-literal-delta-v1'
SOURCE='60d702bf8d83b6c4c8531397a7b770234fd9cf6e'

def state():
    ids,refs,pending=before_gc_literals()
    mp=data.BASE/'PG11490-current-api-web-gc-literal-delta-v1/manifest.json'
    m=data.read_checked(mp,'07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12')
    delta=data.read_checked(mp.parent/'delta.json',m['deltaSha256'])
    scope=set(delta['removedFindingIds'])|{r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
    ids-=set(delta['removedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8910,2787,228]
    return ids,refs,pending

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    old=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    current={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if old['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==2 and all('/src/test/' in p for p in changed)
    sp=data.BASE/'PG11508-metric-http-literal-static-v1/manifest.json'
    static=data.read_checked(sp,'fa8d830558c7799fd70f71104ed49c9cc559e31d3677e73b4a16b12f6072b678')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    fresh=[]
    for path,node in actual:
        assert path in changed and node.get('rule')=='CloseResource'
        identity=original_match(path,node,original,actual)
        fresh.append(dict(id=identity['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],contextManifestSha256=None,status='UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh};scope={r['id'] for r in original if r['path'] in changed}&ids
    assert len(scope)==68 and len(fresh)==len(fresh_ids)==52 and fresh_ids<=scope
    assert not scope&refs and not scope&pending
    removed=scope-fresh_ids
    assert len(removed)==16 and all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    current_ids=ids-removed
    assert len(current_ids)==8894 and len({r['id'] for r in original}-current_ids)==521 and len([i for i in current_ids if i.startswith('PMD-NEW-')])==6
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],
        originalScopeFindings=68,oldScopeFindings=68,newScopeFindings=52,replacedContextWarnings=0,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=8910,sourceDerivedRaw=8894,
        mainRaw=1512,testRaw=7382,totalPriorCorrections=521,newDiagnosticsAdded=0,totalIntroducedDiagnosticsRetained=6,sourceScopeCorrectionsAlreadyCounted=16,
        joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(current_ids-refs),
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
