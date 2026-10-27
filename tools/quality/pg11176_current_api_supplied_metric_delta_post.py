"""Independently reconstruct presentation delta from original ID sets and saved XML."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11176-current-api-supplied-metric-delta-post-v1'
SOURCE='aafcc38d2d48627e10f816dd45bfaeb20bf5e415'


def require(actual,expected):
    if actual!=expected:
        raise ValueError('exact current source and independently reconstructed original sets required')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    mp=data.BASE/'PG11174-current-api-supplied-metric-delta-v1/manifest.json'
    primary=data.read_checked(mp,'cf033c86870cbc11b4ad8900cc244e2158d82cfaebb6dee0453a34018f4201b4')
    delta=data.read_checked(mp.parent/'delta.json',primary['deltaSha256'])
    ids,refs,pending=state()
    for folder,pin in [('PG11058-current-api-request-delta-v1','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390'),
        ('PG11096-current-inbox-value-delta-v1','1c3f95f4b7cb74ea442043405db8d089997e8fa7ed88986fff270aa74a67d2a1'),
        ('PG11122-current-web-pure-value-delta-v1','7964e7e748c4e6d2f2e841ce7666044f399e922579feb8f2bd339837a1c4977d'),
        ('PG11148-current-web-presentation-delta-v1','154c363c7f6d24000346bdec41d970fe02cf39c8f6c7bf13ed2554d8eb9222c1')]:
        p=data.BASE/folder/'manifest.json'
        m=data.read_checked(p,pin)
        d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
        new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=set(d['removedFindingIds'])
        refs=(refs-scope)|new
        pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9134,2739,90]
    normal=data.read_checked(data.BASE/'PG11158-api-metric-fixture-six-compile-v1/manifest.json','580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c')
    old=data.read_checked(data.BASE/'PG11132-web-presentation-six-compile-v1/manifest.json','6ba6867e803958aa47837d6628faeecdf42917be8d23bff7a38b5e1b18579eee')
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items())
    assert {p:h for p,h in hashes.items() if h!=old['begin']['inputHashes'][p]}==delta['sourceInputDelta']
    static_path=data.BASE/'PG11162-api-metric-fixture-static-v1/manifest.json'
    static=data.read_checked(static_path,'d5e5db629b48946657e44567fbfc37c2281ff19a8af5d3a879809b0bc89d7177')
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    context=data.read_checked(data.BASE/'PG11165-api-metric-fixture-context-v1/manifest.json','3b02041b948f03e6993b9bf2603bf943597c252bd8e0375ee5e5c12b3a761813')
    rows=data.read_checked(data.BASE/'PG11165-api-metric-fixture-context-v1/contexts.json',context['contextsSha256'])
    scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    fresh={original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(scope)==55 and len(fresh)==12 and fresh=={r['id'] for r in delta['freshRows']}
    removed=scope-fresh
    assert len(removed)==43 and removed==set(delta['removedFindingIds']) and removed<=ids
    assert all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    reviewed={r['id'] for r in rows}
    assert reviewed==fresh
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    expected=dict(source=SOURCE,raw=len(ids-removed),refs=len(cr),pending=len(cp),withoutReference=len((ids-removed)-cr))
    observed=dict(source=primary['source'],raw=primary['sourceDerivedRaw'],refs=primary['joinedContextWarnings'],
        pending=primary['sourceReboundCurrentWholePending'],withoutReference=primary['noCurrentReferenceInThisJoin'])
    require(observed,expected)
    negatives=0
    for k,v in [('source',None),('raw',9134),('refs',0),('pending',0),('withoutReference',0)]:
        bad=copy.deepcopy(observed)
        bad[k]=v
        try:
            require(bad,expected)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('invented source/count accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),
        counts=expected,metadataNegativeVectors=negatives,sourceCount=1810,sourceChanges=4,mainRaw=1512,testRaw=7579,
        alreadyCountedCorrections43=True,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
