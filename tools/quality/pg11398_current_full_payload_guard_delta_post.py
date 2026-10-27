"""Independently reconstruct one-source current Batch source guard active-ID ID delta from original XML/sets."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11398-current-full-payload-guard-delta-post-v1'
PRIMARY_SHA='63c79243e29df631ae65e6a73b1a0e742b509cfaff1b10a812a2c84eb6fdc5ca'
SOURCE='4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8'


def require(actual,expected):
    if actual!=expected:
        raise ValueError('exact current source and independently reconstructed original sets required')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    mp=data.BASE/'PG11396-current-full-payload-guard-delta-v1/manifest.json'
    primary=data.read_checked(mp,PRIMARY_SHA)
    delta=data.read_checked(mp.parent/'delta.json',primary['deltaSha256'])
    ids,refs,pending=state()
    for folder,pin in [('PG11058-current-api-request-delta-v1','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390'),
        ('PG11096-current-inbox-value-delta-v1','1c3f95f4b7cb74ea442043405db8d089997e8fa7ed88986fff270aa74a67d2a1'),
        ('PG11122-current-web-pure-value-delta-v1','7964e7e748c4e6d2f2e841ce7666044f399e922579feb8f2bd339837a1c4977d'),
        ('PG11148-current-web-presentation-delta-v1','154c363c7f6d24000346bdec41d970fe02cf39c8f6c7bf13ed2554d8eb9222c1'),
        ('PG11174-current-api-supplied-metric-delta-v1','cf033c86870cbc11b4ad8900cc244e2158d82cfaebb6dee0453a34018f4201b4'),
        ('PG11200-current-api-catalog-scalar-pool-delta-v1','1d8c2b3ee0b29dab43497b317aaff2130f07adaf99af8cc7fdfca243f2aea73a'),
        ('PG11228-current-web-supplied-metric-delta-v1','ab671737fc7a03397c1f9a84991fae82d844c2417b5dffa9c41b185d12ef1eee'),
        ('PG11254-current-batch-metric-label-delta-v1','ececd6a74d48472d2ababb2cbb83c8239b023299b1c5f98067cbd4002178a6c2'),
        ('PG11280-current-http-recorder-delta-v1','c7e3191fd0c829b2010adc6ec6ab2f88f0516198358b539bbf1d9e206fef72e3'),
        ('PG11306-current-batch-standard-text-delta-v1','9ba4dac74123a2d5dcc71fa82547ef110f6310fbbbd1521adddf9ab852734dc8'),
        ('PG11338-current-batch-source-guard-delta-v1','7065e59aec2e111a7620f9e543c07e66d1d58d01ee89026dc08af63a778b83e4'),
        ('PG11364-current-api-web-source-guard-delta-v1','bcfe5e858e6f0c5b51d9955f25dba47a4830fd47ef364bb3561c6a7f3be23530')]:
        p=data.BASE/folder/'manifest.json'
        m=data.read_checked(p,pin)
        d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
        new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=set(d['removedFindingIds'])
        refs=(refs-scope)|new
        pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[8924,2755,170]
    normal=data.read_checked(data.BASE/'PG11380-full-payload-guard-six-compile-v1/manifest.json','f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2')
    old=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json','46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items())
    assert {p:h for p,h in hashes.items() if h!=old['begin']['inputHashes'][p]}==delta['sourceInputDelta']
    static_path=data.BASE/'PG11384-full-payload-guard-static-v1/manifest.json'
    static=data.read_checked(static_path,'075bc441fc602c77dfa0b6d7cb6eadcbf4c570893655850f6cb6140c47841a09')
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    context=data.read_checked(data.BASE/'PG11387-full-payload-guard-context-v1/manifest.json','05d0ea5697dfe458af05045250467e076cda73da892e068113e8a142782c3321')
    rows=data.read_checked(data.BASE/'PG11387-full-payload-guard-context-v1/contexts.json',context['contextsSha256'])
    original_scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    scope=original_scope&ids
    assert len(original_scope)==49 and len(scope)==43 and original_scope-scope==set(delta['previouslyRemovedIds'])
    fresh={original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(scope)==43 and len(fresh)==39 and fresh=={r['id'] for r in delta['freshRows']}
    removed=scope-fresh
    assert len(removed)==4 and removed==set(delta['removedFindingIds']) and removed<=ids
    assert all(r['rule']=='CloseResource' for r in original if r['id'] in removed)
    reviewed={r['id'] for r in rows}
    assert len(reviewed)==30 and reviewed|set(context['unclassifiedOriginalIds'])==fresh
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    expected=dict(source=SOURCE,raw=len(ids-removed),refs=len(cr),pending=len(cp),withoutReference=len((ids-removed)-cr))
    observed=dict(source=primary['source'],raw=primary['sourceDerivedRaw'],refs=primary['joinedContextWarnings'],
        pending=primary['sourceReboundCurrentWholePending'],withoutReference=primary['noCurrentReferenceInThisJoin'])
    require(observed,expected)
    negatives=0
    for k,v in [('source',None),('raw',8924),('raw',8914),('refs',0),('pending',0),('withoutReference',0)]:
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
        counts=expected,metadataNegativeVectors=negatives,sourceCount=1810,sourceChanges=3,mainRaw=1512,testRaw=7408,
        alreadyCountedCorrections4=True,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
