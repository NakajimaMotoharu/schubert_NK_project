"""Five current MQ fixture contexts: four finite-own-thread points and one equals(null) oracle."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='6c96b262e88d9863ffb1e883780a249eaa11be27'
OUT=data.BASE/'PG11741-mq-recorder-owner-context-v1'
STATIC_PIN='968d7e43a6d1a2aa9e21269e99899261afe481b90b5c96e8d4315bdd6958e5e1'

def review():
    host=data.read_checked(data.BASE/'PG11736-mq-recorder-literal-host-v1/manifest.json','2ec18eeb50b3f15baff545964708774faa1fae0945c222534daec42ac5cf5efa');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==16
    sp=data.BASE/'PG11738-mq-recorder-literal-static-v1';st=data.read_checked(sp/'manifest.json',STATIC_PIN);raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==point);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);thread=a['rule']=='DoNotUseThreads'
        if thread:
            assert name in ('mqPress006ConcurrentPublicationAndDifferentOwnersDoNotGrowOrShareState','mqRedel007ConcurrentSamePairAndSeparateOwnerHaveExactIndependentCounts')
            assert 'i<64' in compact and 'try(varpool=Executors.newFixedThreadPool(8)){' in compact and 'pool.invokeAll(tasks)' in compact
            assert ('recorder.record(BrokerTopology.ASYNC_WORK,sample);' if 'Pressure' in path else 'recorder.recordDelivery(BrokerTopology.ASYNC_WORK,3);') in compact
            reason='J2EE thread prohibition is not applicable to this dedicated JavaSE JUnit process. Its own eight-worker TWR runs exactly64 finite supplied-value AtomicReference sets or SDK counter increments; invokeAll returns all completed Futures, then result.get reads them. No external waits, JMS, network, authority or service thread is involved. Registry owners are local TWR; current006/007 passes within the whole JVM240s guard. This does not prove broker redelivery or runtime ownership.'
        else:
            assert a['rule']=='EqualsNull' and name=='mqPress008GeneratedSnapshotContractsUseIndependentLongBooleanFoldAndFixedText' and 'assertFalse(value.equals(null));' in compact
            assert 'assertEquals(30607576,value.hashCode());' in compact and 'assertNotEquals(value,collided);' in compact
            reason='Intentional independent Java record equals contract: a nonnull fixed Snapshot must compare false to null, alongside identity/symmetry, each-field differences, fixed hash collisions and fixed text. Replacing equals(null) with an unrelated reference-null assertion would remove this oracle. No application null comparison is being excused. Current008 passes; retain raw warning and exact required-contract reason.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[point:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==5 and sum(r['newSourceReason'] for r in rows)==1
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=5,existingThreadReferencesReauthenticated=4,newEqualsNullReasons=1,rawRetained=5,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
