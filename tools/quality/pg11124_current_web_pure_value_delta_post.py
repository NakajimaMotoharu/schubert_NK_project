"""Independent original ID sets/current XML/source validation, including real lint fail-fast negative."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11058_current_api_request_delta import state
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11124-current-web-pure-value-delta-post-v1'
SOURCE='5fce2af667d8d5cdd9b67da9b02080b105848c28'


def require(value,reference):
    if value!=reference:
        raise ValueError('exact current source and independently reconstructed original sets')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11122-current-web-pure-value-delta-v1/manifest.json'
    primary=data.read_checked(p,'7964e7e748c4e6d2f2e841ce7666044f399e922579feb8f2bd339837a1c4977d')
    delta=data.read_checked(p.parent/'delta.json',primary['deltaSha256'])
    ids,refs,pending=state()
    for folder,pin in [('PG11058-current-api-request-delta-v1','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390'),
        ('PG11096-current-inbox-value-delta-v1','1c3f95f4b7cb74ea442043405db8d089997e8fa7ed88986fff270aa74a67d2a1')]:
        mp=data.BASE/folder/'manifest.json'
        m=data.read_checked(mp,pin)
        d=data.read_checked(mp.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
        new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=set(d['removedFindingIds'])
        refs=(refs-scope)|new
        pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9162,2737,76]
    normal=data.read_checked(data.BASE/'PG11106-web-pure-value-six-compile-v1/manifest.json','77fd485d4718416d3cb75e57e16458d2633289b432bb30a97738d326edcc364b')
    old=data.read_checked(data.BASE/'PG11080-inbox-lifecycle-six-compile-v1/manifest.json','a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641')
    current=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in current.items())
    assert {path:h for path,h in current.items() if h!=old['begin']['inputHashes'][path]}==delta['sourceInputDelta']
    static_path=data.BASE/'PG11110-web-pure-value-static-v1/manifest.json'
    static=data.read_checked(static_path,'d9fb45add999405f77dd42178b344e1da40983e46fa8c3c897088f2db5bb03d6')
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    context=data.read_checked(data.BASE/'PG11113-web-pure-value-context-v1/manifest.json','33b0641d03cfa5bf59029068e376ad180cbf2e1c228d4550741b2cf898b05d0c')
    rows=data.read_checked(data.BASE/'PG11113-web-pure-value-context-v1/contexts.json',context['contextsSha256'])
    scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    fresh={original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(scope)==29 and len(fresh)==10 and fresh=={r['id'] for r in delta['freshRows']}
    removed=scope-fresh
    assert len(removed)==19 and removed==set(delta['removedFindingIds']) and removed<=ids
    reviewed={r['id'] for r in rows}
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    expected=dict(source=SOURCE,raw=len(ids-removed),refs=len(cr),pending=len(cp),withoutReference=len((ids-removed)-cr))
    actual_counts=dict(source=primary['source'],raw=primary['sourceDerivedRaw'],refs=primary['joinedContextWarnings'],
        pending=primary['sourceReboundCurrentWholePending'],withoutReference=primary['noCurrentReferenceInThisJoin'])
    require(actual_counts,expected)
    negatives=0
    for k,v in [('source','old'),('raw',9162),('refs',0),('pending',0),('withoutReference',0)]:
        bad=copy.deepcopy(actual_counts)
        bad[k]=v
        try:
            require(bad,expected)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('invented source/count accepted')
    producer=data.ROOT/'tools/quality/pg11122_current_web_pure_value_delta.py'
    original_tool=producer.read_text().replace('import g07_host_class_provenance_inputs as data','from pathlib import Path\nimport g07_host_class_provenance_inputs as data',1)
    assert data.sha(original_tool.encode())==primary['invocation']['entrypointSha256']=='979b25b9ea510782d47f30ef2dc3ef0239700b4f6e04f5fb3a4bfba248661a48'
    negative_path=data.BASE/'PG11123-checked-entry-preflight-negative-v1/manifest.json'
    negative=__import__('json').loads(negative_path.read_bytes())
    assert negative['actualExit']==1 and negative['printedResult']['lintExit']==1 and negative['printedResult']['bodyStarted'] is False
    assert negative['printedResult']['entrySha256']==data.sha(original_tool.encode()) and not negative['producerReplayed']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(p.read_bytes()),
        counts=expected,metadataNegativeVectors=negatives,originalProducerLintPassed=False,originalProducerBodyExit=0,
        unusedImportOnlyInverseVerified=True,checkedEntryRealNegativeSha256=data.sha(negative_path.read_bytes()),
        checkedRunnerSha256=data.sha((data.ROOT/'tools/quality/pg11123_checked_python_entry.py').read_bytes()),
        sourceCount=1810,sourceChanges=3,mainRaw=1512,testRaw=7631,alreadyCountedCorrections19=True,
        productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
