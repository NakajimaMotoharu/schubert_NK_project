"""Twenty current own-fixture Thread contexts reauthenticated; all raw retained."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='69d50093df9e655a39eadcd7a392646ff65bfbb0'
OUT=data.BASE/'PG11841-mq-media-collector-owner-context-v1'

def review():
    host=data.read_checked(data.BASE/'PG11836-mq-media-collector-value-host-v1/manifest.json','e2911e57d15ba6dc00b7e68ffe075b4f2edb2e05e9ffadf3e2d4e72cd281016d');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==16
    sp=data.BASE/'PG11838-mq-media-collector-value-static-v1';st=data.read_checked(sp/'manifest.json','1c5b7a45fd5c3a1b3b3d4ab49355213784cdd36d4cb5068da46eaaeeb67d45ab');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;assert a['rule']=='DoNotUseThreads';lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==point);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);prefix='mqConn' if 'MqPressure' in path else 'mediaConn'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method'].startswith(prefix+('006' if name=='await' else '007' if name.startswith(prefix+'007') else '006')))
        if name=='await':
            assert '.await(5,TimeUnit.SECONDS)' in compact and 'Thread.currentThread().interrupt()' in compact
            kind='FINITE_LATCH_AND_RESTORED_INTERRUPT';reason='The test-only helper bounds its own latch wait at five seconds, asserts the result, restores interruption and fails the fixture. Caller006 releases its own latch in finally; this is neither a server thread nor a retry/normalization of a business failure.'
        elif name.startswith(prefix+'006'):
            assert 'Executors.newFixedThreadPool(2)' in compact and 'Thread.State.BLOCKED' in compact and 'TimeUnit.SECONDS.toNanos(5)' in compact and 'finally{release.countDown();}' in compact and '.get(5,TimeUnit.SECONDS)' in compact
            kind='OWN_TWO_WORKER_BLOCKED_PUBLICATION';reason='Dedicated JavaSE JUnit owns two finite workers in TWR. Its latch holds the first supplied read; the second actual owned thread must be BLOCKED within a five-second monotonic deadline. finally releases the gate and both results have five-second get bounds. This observes one concrete schedule, not all schedules or production lifecycle; source callbacks do memory observations only.'
        else:
            assert name.startswith(prefix+'007') and 'Executors.newFixedThreadPool(8)' in compact and ('i<64' in compact or 'index<64' in compact) and 'executor.invokeAll(tasks)' in compact and '.get(5,TimeUnit.SECONDS)' in compact
            kind='OWN_FINITE64_SUPPLIED_VALUE_TASKS';reason='Dedicated JavaSE JUnit owns eight TWR workers and exactly64 finite supplied-value callbacks. Independent identity-keyed input vectors and separate caller-owned registries detect mixed owners; invokeAll completes before bounded gets. No external IO, server executor or production resource owner is involved.'
        assert name=='await' or name==case['method'];assert any(c['classname']==case['className'] and c['name']==case['method'] and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[point:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==20
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=20,existingThreadReferencesReauthenticated=20,newSourceReasons=0,rawRetained=20,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
