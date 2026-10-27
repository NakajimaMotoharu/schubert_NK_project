"""Independent original/new-ID inventory and measured eight-literal removal; no PT/analyzer replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11054_api_request_context import attrs,original_match

OUT=data.BASE/'PG11492-current-api-web-gc-literal-delta-post-v1'
SOURCE='d1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7'

def require(actual,expected):
    if actual!=expected:
        raise ValueError('current source and exact original/new diagnostic sets required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=historical()
    previous_path=data.BASE/'PG11460-current-gc-fake-guard-delta-v1/manifest.json'
    previous=data.read_checked(previous_path,'3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2')
    pd=data.read_checked(previous_path.parent/'delta.json',previous['deltaSha256'])
    scope=set(pd['removedFindingIds'])|{r['id'] for r in pd['freshRows']}
    reviewed={r['id'] for r in pd['freshRows'] if r['contextManifestSha256']}
    ids=(ids-set(pd['removedFindingIds']))|set(pd['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8918,2787,228]
    mp=data.BASE/'PG11490-current-api-web-gc-literal-delta-v1/manifest.json'
    manifest=data.read_checked(mp,'07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12')
    delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    old=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json','0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert {p:h for p,h in hashes.items() if old['begin']['inputHashes'][p]!=h}==delta['sourceInputDelta']
    sp=data.BASE/'PG11478-api-web-gc-literal-static-v1/manifest.json'
    static=data.read_checked(sp,'1a50d80fd30b1809f89a55e0bab3d9b51100f9e89251970d71bdd78aab5a05bd')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    discoveries=data.read_checked(data.ROOT/pd['newDiagnosticRegistryPath'],pd['newDiagnosticRegistrySha256'])
    observed_ids={}
    for path,node in actual:
        matches=[r for r in discoveries if r['path']==path and attrs(r['attributes'])==attrs(node.attrib) and r['descriptor']['message']==''.join(node.itertext()).strip()]
        assert len(matches)<=1
        identity=matches[0]['id'] if matches else original_match(path,node,original,actual)['id']
        observed_ids[(path,tuple(sorted(node.attrib.items())))]=identity
    assert len(observed_ids)==len(set(observed_ids.values()))==24
    fresh={r['id'] for r in delta['freshRows']}
    assert fresh==set(observed_ids.values())
    for row in delta['freshRows']:
        assert observed_ids[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==hashes[row['path']]
    changed=delta['sourceInputDelta']
    original_scope={r['id'] for r in original if r['path'] in changed}
    new_scope={r['id'] for r in discoveries if r['path'] in changed}
    scope=(original_scope|new_scope)&ids
    assert len(original_scope)==28 and len(new_scope)==4 and len(scope)==32 and new_scope<=fresh
    removed=scope-fresh
    assert len(removed)==8 and removed==set(delta['removedFindingIds']) and not delta['addedFindingIds']
    assert all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    current=ids-removed
    assert {r['id'] for r in discoveries}<=current
    cp=data.BASE/'PG11481-api-web-gc-literal-context-v1/manifest.json'
    context=data.read_checked(cp,'06a16aa30c664c67ff9bf24005406af9ab3fc2dfd74097c58328a08ec54b6d14')
    contexts=data.read_checked(cp.parent/'contexts.json',context['contextsSha256'])
    reviewed={r['id'] for r in contexts};assert reviewed==fresh
    cr=(refs-scope)|reviewed;cpending=(pending-scope)|reviewed
    expected=dict(source=SOURCE,raw=len(current),refs=len(cr),pending=len(cpending),withoutReference=len(current-cr),corrections=len({r['id'] for r in original}-current),newRetained=len({r['id'] for r in discoveries}&current))
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],
        withoutReference=manifest['noCurrentReferenceInThisJoin'],corrections=manifest['totalPriorCorrections'],newRetained=manifest['totalIntroducedDiagnosticsRetained'])
    require(observed,expected)
    for key,value in [('source','old'),('raw',8918),('raw',8904),('refs',0),('pending',0),('withoutReference',0),('corrections',511),('newRetained',0)]:
        bad=copy.deepcopy(observed);bad[key]=value
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('lost diagnostic or false correction accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,
        metadataNegativeVectors=8,sourceCount=1810,sourceChanges=2,mainRaw=1512,testRaw=7398,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
