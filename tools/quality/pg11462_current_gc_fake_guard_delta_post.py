"""Independent historical ID-chain reconstruction including added-diagnostic registry."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11058_current_api_request_delta import state
from pg11054_api_request_context import attrs,original_match
from public_java_digest_provenance import LEX

OUT=data.BASE/"PG11462-current-gc-fake-guard-delta-post-v1"
SOURCE="495313cd8e724d5f1906fca64d9d9fd3516aae50"

def historical():
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
        ('PG11364-current-api-web-source-guard-delta-v1','bcfe5e858e6f0c5b51d9955f25dba47a4830fd47ef364bb3561c6a7f3be23530'),
        ('PG11396-current-full-payload-guard-delta-v1','63c79243e29df631ae65e6a73b1a0e742b509cfaff1b10a812a2c84eb6fdc5ca')]:
        p=data.BASE/folder/'manifest.json'
        m=data.read_checked(p,pin)
        d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
        new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=set(d['removedFindingIds'])
        refs=(refs-scope)|new
        pending=(pending-scope)|new

    p=data.BASE/"PG11428-current-api-web-payload-literal-delta-v1/manifest.json"
    m=data.read_checked(p,"634c62599b0b66df92dd63a7038298153ff4201c10feb41d3925b304be5cd78d")
    d=data.read_checked(p.parent/"delta.json",m["deltaSha256"])
    ids-=set(d["removedFindingIds"])
    scope=set(d["removedFindingIds"])|{r["id"] for r in d["freshRows"]}
    reviewed={r["id"] for r in d["freshRows"] if r["contextManifestSha256"]}
    refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8912,2757,194]
    return ids,refs,pending

def require(value,reference):
    if value!=reference:
        raise ValueError('independent current ID counts and source required')

def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=historical()
    mp=data.BASE/'PG11460-current-gc-fake-guard-delta-v1/manifest.json'
    manifest=data.read_checked(mp,'3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2')
    delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json','0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    previous=data.read_checked(data.BASE/'PG11412-api-web-payload-literal-six-compile-v1/manifest.json','b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d')
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert {p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p]!=h}==delta['sourceInputDelta']
    static_path=data.BASE/'PG11448-gc-fake-guard-static-v1/manifest.json'
    static=data.read_checked(static_path,'4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185')
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256'] and static['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    discoveries=data.read_checked(data.ROOT/delta['newDiagnosticRegistryPath'],delta['newDiagnosticRegistrySha256'])
    new_nodes=sorted(((p,n) for p,n in actual if re.fullmatch(r'(api|web|batch)gc01[56]\w*',n.get('method',''))),key=lambda item:(item[0],item[1].get('method')))
    assert len(new_nodes)==len(discoveries)==6
    actual_ids={}
    for index,(path,node) in enumerate(new_nodes,1):
        row=discoveries[index-1]
        descriptor=dict(sourceDiscovered=SOURCE,path=path,rule=node.get('rule'),method=node.get('method'),variable='resource',message=''.join(node.itertext()).strip())
        assert node.get('rule')=='CloseResource' and node.get('variable')=='resource'
        assert row['id']==f'PMD-NEW-PG11448-{index:03d}' and row['descriptor']==descriptor and row['sourceSha256']==hashes[path]
        assert row['rowSha256']==data.sha(json.dumps(descriptor,sort_keys=True).encode()) and row['id'] not in ids
        actual_ids[(path,tuple(sorted(node.attrib.items())))]=row['id']
    for path,node in actual:
        key=path,tuple(sorted(node.attrib.items()))
        if key in actual_ids:
            continue
        if node.get('rule')=='AvoidDuplicateLiterals':
            message=' '.join((node.text or '').split())
            match=re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line ([0-9]+)',message)
            assert match
            text=(data.ROOT/path).read_text();occurrences=[m for m in LEX.finditer(text) if m.group()=='"'+match[1]+'"']
            assert len(occurrences)==int(match[2]) and text[:occurrences[0].start()].count('\n')+1==int(match[3])==int(node.get('beginline'))
            semantic=re.sub(r'first occurrence is on line [0-9]+$','first occurrence is on line #',message)
            matches=[r for r in original if r['path']==path and r['rule']==node.get('rule') and attrs(r['attributes'])==attrs(node.attrib)
                and re.sub(r'first occurrence is on line [0-9]+$','first occurrence is on line #',' '.join(r['message'].split()))==semantic]
            assert len(matches)==1
            identity=matches[0]['id']
        else:
            identity=original_match(path,node,original,actual)['id']
        actual_ids[key]=identity
    assert len(actual_ids)==44 and len(set(actual_ids.values()))==44
    fresh={r['id'] for r in delta['freshRows']}
    for row in delta['freshRows']:
        assert actual_ids[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==hashes[row['path']]
    assert fresh==set(actual_ids.values())
    original_scope={r['id'] for r in original if r['path'] in delta['sourceInputDelta']}
    old_scope=original_scope&ids
    new_ids={r['id'] for r in discoveries}
    assert len(old_scope)==38 and fresh==old_scope|new_ids and not delta['removedFindingIds'] and set(delta['addedFindingIds'])==new_ids
    context_path=data.BASE/'PG11451-gc-fake-guard-context-v3/manifest.json'
    context=data.read_checked(context_path,'6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb')
    contexts=data.read_checked(context_path.parent/'contexts.json',context['contextsSha256'])
    reviewed={r['id'] for r in contexts}
    assert len(reviewed)==36 and reviewed|set(context['unclassifiedOriginalIds'])==fresh
    current=ids|new_ids;cr=(refs-old_scope)|reviewed;cp=(pending-old_scope)|reviewed
    expected=dict(source=SOURCE,raw=len(current),refs=len(cr),pending=len(cp),withoutReference=len(current-cr),corrections=len({r['id'] for r in original}-current),newAdded=len(new_ids))
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],
        withoutReference=manifest['noCurrentReferenceInThisJoin'],corrections=manifest['totalPriorCorrections'],newAdded=manifest['newDiagnosticsAdded'])
    require(observed,expected)
    for key,value in [('source','old'),('raw',8912),('raw',8900),('refs',0),('pending',0),('withoutReference',0),('corrections',491),('newAdded',0)]:
        bad=copy.deepcopy(observed);bad[key]=value
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('missing diagnostic or false correction accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,
        metadataNegativeVectors=8,sourceCount=1810,sourceChanges=3,mainRaw=1512,testRaw=7406,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
