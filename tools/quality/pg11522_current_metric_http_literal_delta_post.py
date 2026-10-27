"""Independent historical sets plus current XML; unclassified52 are not context-reviewed or suppressed."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11054_api_request_context import original_match

SOURCE='60d702bf8d83b6c4c8531397a7b770234fd9cf6e'
OUT=data.BASE/'PG11522-current-metric-http-literal-delta-post-v1'

def require(value,expected):
    if value!=expected:
        raise ValueError('exact current source and independent original/new ID sets required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,pending=historical()
    for folder,pin in [('PG11460-current-gc-fake-guard-delta-v1','3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2'),('PG11490-current-api-web-gc-literal-delta-v1','07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8910,2787,228]
    mp=data.BASE/'PG11520-current-metric-http-literal-delta-v1/manifest.json'
    manifest=data.read_checked(mp,'e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab')
    delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    old=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert {p:h for p,h in hashes.items() if old['begin']['inputHashes'][p]!=h}==delta['sourceInputDelta']
    sp=data.BASE/'PG11508-metric-http-literal-static-v1/manifest.json';static=data.read_checked(sp,'fa8d830558c7799fd70f71104ed49c9cc559e31d3677e73b4a16b12f6072b678')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    observed_ids={(path,tuple(sorted(n.attrib.items()))):original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(observed_ids)==len(set(observed_ids.values()))==52
    fresh={r['id'] for r in delta['freshRows']}
    assert fresh==set(observed_ids.values())
    for row in delta['freshRows']:
        assert observed_ids[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==hashes[row['path']]
        assert row['status']=='UNCLASSIFIED_RETAINED' and row['contextManifestSha256'] is None and not row['oldRuntimeReassigned']
    scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}&ids
    assert len(scope)==68 and not scope&refs and not scope&pending
    removed=scope-fresh;assert len(removed)==16 and removed==set(delta['removedFindingIds']) and not delta['addedFindingIds']
    assert all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in removed)
    current=ids-removed
    expected=dict(source=SOURCE,raw=len(current),refs=len(refs),pending=len(pending),withoutReference=len(current-refs),corrections=len({r['id'] for r in original}-current),newRetained=len([i for i in current if i.startswith('PMD-NEW-')]))
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],withoutReference=manifest['noCurrentReferenceInThisJoin'],corrections=manifest['totalPriorCorrections'],newRetained=manifest['totalIntroducedDiagnosticsRetained'])
    require(observed,expected)
    for key,value in [('source','old'),('raw',8910),('raw',8888),('refs',2839),('pending',280),('withoutReference',0),('corrections',527),('newRetained',0)]:
        bad=copy.deepcopy(observed);bad[key]=value
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invented classification or dropped new diagnostic accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,
        metadataNegativeVectors=8,sourceCount=1810,sourceChanges=2,unclassifiedCurrentScope=52,mainRaw=1512,testRaw=7382,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
