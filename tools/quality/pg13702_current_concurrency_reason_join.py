"""Five exact-source existing static reasons, not new reasons or runtime qualifications."""
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match
from pmd_source_span_ascii import span
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13702-current-concurrency-reason-join-v1'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
BUFFER = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/WipingByteArrayOutputStream.java'
TRACE = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestTrace.java'
TARGETS = {BUFFER:dict(rule='AvoidSynchronizedAtMethodLevel',sha256='1f751a0267c7d9f894806d67e5b9b3c05955038353d6f6bd6a44cfe3bd1217de',owner='WBS-P006-01',count=4),TRACE:dict(rule='AvoidUsingVolatile',sha256='e913d995a5cd7443c96fede3171b2cc241b5340f952532c382e5246180382ad1',owner='WBS-P006-03',count=1)}
OLD = {BUFFER:('PG5920-buffer-map-contracts-v2','7a874e49cbcc7946f9651784dbd092af3a791c035f152761e3619e2133bd365e','decisions.json','decisionsSha256'),TRACE:('PG6122-web-lifecycle-review-v1','de556946d7407b1e0ddc7925fffb7aaa33c9ebf3b7adcb27d75183ea4797cd49','reviews.json','reviewsSha256')}
IDS = {'PMD-00131','PMD-00132','PMD-00133','PMD-00134','PMD-07317'}

def rows():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1])
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1])
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    raw = (data.BASE/MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(raw) == measured['reports']['pmd']['sha256']
    actual = [(str(__import__('pathlib').Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2] == 'file' for n in f if n.tag.rpartition('}')[2] == 'violation']
    result = []
    for path,t in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == t['sha256']
        assert {r['sourceSha256'] for r in facts if r['path'] == path} == {t['sha256']}
        name,pin,filename,key = OLD[path];old = data.read_checked(data.BASE/name/'manifest.json',pin);assert old['actualExit'] == 0
        previous = data.read_checked(data.BASE/name/filename,old[key])
        candidates = [r for r in previous if r['sourcePath'] == path and r['rule'] == t['rule']]
        assert len(candidates) == t['count']
        owner = canonical(path,logical);assert owner['canonicalOwner'] == owner['canonicalCostOwner'] == t['owner']
        selected = [(p,n) for p,n in actual if p == path and n.get('rule') == t['rule']];assert len(selected) == t['count']
        for _,node in selected:
            identity = original_match(path,node,original,actual)
            old_row, = [r for r in candidates if all(r[k] == node.get(k) for k in ['beginline','endline','begincolumn','endcolumn'])]
            assert old_row['sourceSha256'] == t['sha256'] and old_row['reason'] and old_row['rawWarningRetained']
            start,end,value = span(text,dict(node.attrib));assert value == node.get('method',node.get('variable'))
            result.append(dict(id=identity['id'],path=path,source=SOURCE,sourceSha256=t['sha256'],rule=t['rule'],attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),priorManifest=name,priorManifestSha256=pin,priorDecisionSha256=data.sha(json.dumps(old_row,sort_keys=True).encode()),reason=old_row['reason'],reasonReused=True,newReason=False,rawRetained=True,currentWholeJoinPending=True,historicalRuntimeTransferred=False,currentRuntimeQualification=False,productTestsExecuted=0,**owner))
    assert {r['id'] for r in result} == IDS and len(result) == 5
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists()
    value = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=value))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=5,newReasons=0,reusedReasons=5,rawRetained=5,currentWholeJoinPending=True,productTestsExecuted=0,sourceChanged=False,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
