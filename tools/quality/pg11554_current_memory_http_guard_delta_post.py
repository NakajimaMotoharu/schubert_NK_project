"""Independent historical active-ID reconstruction and two newly observed cleanup descriptors."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11054_api_request_context import original_match

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11554-current-memory-http-guard-delta-post-v1'

def require(value,expected):
    if value!=expected:
        raise ValueError('exact current source and independently reconstructed original/new diagnostic inventory required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=historical()
    for folder,pin in [('PG11460-current-gc-fake-guard-delta-v1','3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2'),
        ('PG11490-current-api-web-gc-literal-delta-v1','07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12'),('PG11520-current-metric-http-literal-delta-v1','e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8894,2787,228]
    mp=data.BASE/'PG11552-current-memory-http-guard-delta-v1/manifest.json'
    manifest=data.read_checked(mp,'27544edc188e17ec6ec38a7222dc8403298827e25762c67e56cee865e7b1e0bc');delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11536-memory-http-guard-six-compile-v1/manifest.json','038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936')
    old=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert {p:h for p,h in hashes.items() if old['begin']['inputHashes'][p]!=h}==delta['sourceInputDelta']
    sp=data.BASE/'PG11540-memory-http-guard-static-v1/manifest.json';static=data.read_checked(sp,'b853cc3070e3a836a251a2118fdeb8ef038680be336e929fde1b604fb385314b')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    discoveries=data.read_checked(data.ROOT/delta['newDiagnosticRegistryPath'],delta['newDiagnosticRegistrySha256'])
    new_nodes=sorted(((p,n) for p,n in actual if re.fullmatch(r'(api|web)mhttp023\w*',n.get('method',''))),key=lambda item:(item[0],item[1].get('method')))
    assert len(new_nodes)==len(discoveries)==2;actual_ids={}
    for index,(path,node) in enumerate(new_nodes,1):
        row=discoveries[index-1];descriptor=dict(sourceDiscovered=SOURCE,path=path,rule=node.get('rule'),method=node.get('method'),variable='exchange',message=''.join(node.itertext()).strip())
        assert node.get('rule')=='CloseResource' and node.get('variable')=='exchange'
        assert row['id']==f'PMD-NEW-PG11540-{index:03d}' and row['descriptor']==descriptor and row['sourceSha256']==hashes[path] and row['id'] not in ids
        assert row['rowSha256']==data.sha(json.dumps(descriptor,sort_keys=True).encode())
        actual_ids[(path,tuple(sorted(node.attrib.items())))]=row['id']
    for path,node in actual:
        key=path,tuple(sorted(node.attrib.items()))
        if key not in actual_ids:
            actual_ids[key]=original_match(path,node,original,actual)['id']
    assert len(actual_ids)==len(set(actual_ids.values()))==54
    fresh={r['id'] for r in delta['freshRows']};assert fresh==set(actual_ids.values())
    for row in delta['freshRows']:
        assert actual_ids[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==hashes[row['path']]
    original_scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']};old_scope=original_scope&ids;new_ids={r['id'] for r in discoveries}
    assert len(original_scope)==68 and len(old_scope)==52 and fresh==old_scope|new_ids
    assert not old_scope&refs and not old_scope&pending and not delta['removedFindingIds'] and set(delta['addedFindingIds'])==new_ids
    cp=data.BASE/'PG11543-memory-http-guard-context-v1/manifest.json';context=data.read_checked(cp,'db8f662a118b6e798b982992cc70c6819366156e5c5974f79bd91238071680b6')
    contexts=data.read_checked(cp.parent/'contexts.json',context['contextsSha256']);reviewed={r['id'] for r in contexts};assert reviewed==fresh
    current=ids|new_ids;cr=(refs-old_scope)|reviewed;cpending=(pending-old_scope)|reviewed
    expected=dict(source=SOURCE,raw=len(current),refs=len(cr),pending=len(cpending),withoutReference=len(current-cr),corrections=len({r['id'] for r in original}-current),newRetained=len([i for i in current if i.startswith('PMD-NEW-')]))
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],withoutReference=manifest['noCurrentReferenceInThisJoin'],corrections=manifest['totalPriorCorrections'],newRetained=manifest['totalIntroducedDiagnosticsRetained'])
    require(observed,expected)
    for key,value in [('source','old'),('raw',8894),('raw',8888),('refs',0),('pending',0),('withoutReference',0),('corrections',519),('newRetained',6)]:
        bad=copy.deepcopy(observed);bad[key]=value
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('lost new diagnostics or false correction accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,
        metadataNegativeVectors=8,sourceCount=1810,sourceChanges=2,mainRaw=1512,testRaw=7384,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
