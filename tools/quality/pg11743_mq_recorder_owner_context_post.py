"""Independent current XML/span/case/owner checks with eight metadata negatives, no product replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='6c96b262e88d9863ffb1e883780a249eaa11be27'
OUT=data.BASE/'PG11743-mq-recorder-owner-context-post-v1'
PIN='0a1e03a22c825d6ea788a884e4c6e55104ac16abf41194b28bcc3193e5181245'

def main():
    invocation=capture(__file__);assert not OUT.exists();cp=data.BASE/'PG11741-mq-recorder-owner-context-v1';m=data.read_checked(cp/'manifest.json',PIN);review=data.read_checked(cp/'review.json',m['reviewSha256'])
    host=data.read_checked(data.BASE/'PG11736-mq-recorder-literal-host-v1/manifest.json','2ec18eeb50b3f15baff545964708774faa1fae0945c222534daec42ac5cf5efa')
    sp=data.BASE/'PG11738-mq-recorder-literal-static-v1';st=data.read_checked(sp/'manifest.json','968d7e43a6d1a2aa9e21269e99899261afe481b90b5c96e8d4315bdd6958e5e1');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual={(str(Path(f.get('name')).relative_to(data.ROOT)),tuple(sorted(n.attrib.items()))) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);thread=a['rule']=='DoNotUseThreads'
        expected_case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        expected=dict(source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=expected_case,disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason') or (path,tuple(sorted(a.items()))) not in actual:raise ValueError('exact current source/case/span/owner contract required')
        assert data.sha(text.encode())==expected['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        if thread:
            assert name in ('mqPress006ConcurrentPublicationAndDifferentOwnersDoNotGrowOrShareState','mqRedel007ConcurrentSamePairAndSeparateOwnerHaveExactIndependentCounts')
            assert 'i<64' in compact and 'try(varpool=Executors.newFixedThreadPool(8)){' in compact and 'pool.invokeAll(tasks)' in compact and 'result.get()' in compact
            assert ('recorder.record(BrokerTopology.ASYNC_WORK,sample);' if 'Pressure' in path else 'recorder.recordDelivery(BrokerTopology.ASYNC_WORK,3);') in compact
        else:
            assert a['rule']=='EqualsNull' and name=='mqPress008GeneratedSnapshotContractsUseIndependentLongBooleanFoldAndFixedText'
            assert 'assertFalse(value.equals(null));' in compact and 'assertEquals(30607576,value.hashCode());' in compact and 'assertNotEquals(value,collided);' in compact
        assert any(c['classname']==expected_case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(actual)==len({r['id'] for r in rows})==5 and sum(r['newSourceReason'] for r in rows)==1
    for row in rows:validate(row)
    first=rows[0];negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(first);bad[field]=value;assert bad!=first
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid source contract metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=5,existingThreadReferencesReauthenticated=4,newEqualsNullReasons=1,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
