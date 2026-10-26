"""Independent original ID union, actual empty XML and current-source accounting."""
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT=data.BASE/'PG11098-current-inbox-value-delta-post-v1'
SOURCE='f97723798f3f71a9112b4bbecfba531dba9b34b6'


def require(value,reference):
    if value!=reference:
        raise ValueError('exact original ID union and current empty four-source diagnostics required')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    path=data.BASE/'PG11096-current-inbox-value-delta-v1/manifest.json'
    primary=data.read_checked(path,'1c3f95f4b7cb74ea442043405db8d089997e8fa7ed88986fff270aa74a67d2a1')
    delta=data.read_checked(path.parent/'delta.json',primary['deltaSha256'])
    base_path=data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    base=data.read_checked(base_path,'0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    index=data.read_checked(base_path.parent/'current-index.json',base['currentIndexSha256'])
    ids={r['id'] for r in index}
    for folder,pin in [
        ('PG10910-current-f03-web-metric-delta-v1','7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66'),
        ('PG10968-current-form-delta-v1','ab7756868701839934166c59efb053380f40467f4c497815385de376357d6e33'),
        ('PG11028-current-remaining-form-delta-v1','a1b84233e2748889d2e659c3b611d6f8560685f5e7d84edb9a3e2018e9bb6f49'),
        ('PG11058-current-api-request-delta-v1','369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390')]:
        prior_path=data.BASE/folder/'manifest.json'
        m=data.read_checked(prior_path,pin)
        d=data.read_checked(prior_path.parent/'delta.json',m['deltaSha256'])
        removed=set(d['removedFindingIds'])
        assert removed<=ids
        ids-=removed
    assert len(ids)==9190
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    normal=data.read_checked(data.BASE/'PG11080-inbox-lifecycle-six-compile-v1/manifest.json','a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641')
    old=data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
    current=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in current.items())
    assert {p:h for p,h in current.items() if h!=old['begin']['inputHashes'][p]}==delta['sourceInputDelta']
    removed={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    assert removed==set(delta['removedFindingIds']) and len(removed)==28 and removed<=ids and not delta['freshRows']
    static_path=data.BASE/'PG11084-inbox-lifecycle-static-v1/manifest.json'
    static=data.read_checked(static_path,'d7aaaad5997bd39faeb386dcdfbc5c605c8f42cdf5c51f6eea9fe7423d6a8404')
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        raw=(static_path.parent/(label+'.xml')).read_bytes()
        assert data.sha(raw)==static['reports'][label]['sha256']
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in (tag,'configerror')]
    ids-=removed
    reference=dict(source=SOURCE,raw=len(ids),main=sum(r['id'] in ids and r['sourceKind']=='MAIN' for r in original),
        test=sum(r['id'] in ids and r['sourceKind']=='TEST' for r in original),removed=sorted(removed),fresh=[])
    actual=dict(source=primary['source'],raw=primary['sourceDerivedRaw'],main=primary['mainRaw'],test=primary['testRaw'],
        removed=delta['removedFindingIds'],fresh=delta['freshRows'])
    require(actual,reference)
    negatives=0
    for key,value in [('source','old'),('raw',9190),('main',0),('test',0),('removed',delta['removedFindingIds'][:-1]),('fresh',[{}])]:
        bad=copy.deepcopy(actual)
        bad[key]=value
        try:
            require(bad,reference)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('invented source/finding accounting')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(path.read_bytes()),
        sourceDerivedRaw=len(ids),mainRaw=1512,testRaw=7650,metadataNegativeVectors=negatives,sourceCount=1810,sourceChanges=4,
        alreadyCountedCorrections28=True,joinedContextWarnings=2737,sourceReboundCurrentWholePending=76,noCurrentReferenceInThisJoin=6425,
        productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
