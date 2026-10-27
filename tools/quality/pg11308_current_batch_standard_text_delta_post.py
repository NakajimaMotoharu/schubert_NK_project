"""Independently reconstruct six-source current Batch standard-to-text ID delta from original XML/sets."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11308-current-batch-standard-text-delta-post-v1'
SOURCE='d431ad964355c4e5c602fcb94fe0182da6ae3a61'


def require(actual,expected):
    if actual!=expected:
        raise ValueError('exact current source and independently reconstructed original sets required')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    mp=data.BASE/'PG11306-current-batch-standard-text-delta-v1/manifest.json'
    primary=data.read_checked(mp,'9ba4dac74123a2d5dcc71fa82547ef110f6310fbbbd1521adddf9ab852734dc8')
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
        ('PG11280-current-http-recorder-delta-v1','c7e3191fd0c829b2010adc6ec6ab2f88f0516198358b539bbf1d9e206fef72e3')]:
        p=data.BASE/folder/'manifest.json'
        m=data.read_checked(p,pin)
        d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
        new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=set(d['removedFindingIds'])
        refs=(refs-scope)|new
        pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9000,2754,138]
    normal=data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json','e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
    old=data.read_checked(data.BASE/'PG11264-http-recorder-fixture-six-compile-v1/manifest.json','87b29c22a2f3b612936173d8633cd67201368bc1f711938a0f1e834624f17d9f')
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items())
    assert {p:h for p,h in hashes.items() if h!=old['begin']['inputHashes'][p]}==delta['sourceInputDelta']
    static_path=data.BASE/'PG11294-batch-standard-text-fixture-static-v1/manifest.json'
    static=data.read_checked(static_path,'8ebe64d8773c98c27db1180a4187829280886700c487c6c96021bdec9807ab63')
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    context=data.read_checked(data.BASE/'PG11297-batch-standard-text-fixture-context-v1/manifest.json','0bc9214c567afda1d18ad4441b016c7ec780f59ec7ef31f5d118d015cf8f4be4')
    rows=data.read_checked(data.BASE/'PG11297-batch-standard-text-fixture-context-v1/contexts.json',context['contextsSha256'])
    scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    fresh={original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(scope)==79 and len(fresh)==52 and fresh=={r['id'] for r in delta['freshRows']}
    removed=scope-fresh
    assert len(removed)==27 and removed==set(delta['removedFindingIds']) and removed<=ids
    assert all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    reviewed={r['id'] for r in rows}
    assert len(reviewed)==20 and reviewed|set(context['unclassifiedOriginalIds'])==fresh
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    expected=dict(source=SOURCE,raw=len(ids-removed),refs=len(cr),pending=len(cp),withoutReference=len((ids-removed)-cr))
    observed=dict(source=primary['source'],raw=primary['sourceDerivedRaw'],refs=primary['joinedContextWarnings'],
        pending=primary['sourceReboundCurrentWholePending'],withoutReference=primary['noCurrentReferenceInThisJoin'])
    require(observed,expected)
    negatives=0
    for k,v in [('source',None),('raw',9000),('refs',0),('pending',0),('withoutReference',0)]:
        bad=copy.deepcopy(observed)
        bad[k]=v
        try:
            require(bad,expected)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('invented source/count accepted')
    assert not Path('/home/mini/codex/project1/tools/quality/pg11254_current_batch_metric_label_delta.py').exists()
    assert (data.ROOT/'tools/quality/pg11254_current_batch_metric_label_delta.py').is_file()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),
        counts=expected,metadataNegativeVectors=negatives,sourceCount=1810,sourceChanges=6,mainRaw=1512,testRaw=7461,
        alreadyCountedCorrections27=True,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
