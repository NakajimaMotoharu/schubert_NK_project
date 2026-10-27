"""Six current finite-thread reauth and six exact-snapshot identity reasons, raw retained."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='60f62bd5dffb11e9943fc7578d9bddf380f8003c'
OUT=data.BASE/'PG11811-job-outbox-value-owner-context-v1'

def review():
    host=data.read_checked(data.BASE/'PG11806-job-outbox-value-literal-host-v1/manifest.json','89a9ea21cc85b393ae250b02a92b4d5fb76fc1682a053c2d03e175fa62ad1e98');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==28
    sp=data.BASE/'PG11808-job-outbox-value-literal-static-v1';st=data.read_checked(sp/'manifest.json','c7d692599949d97030a84d4612b8110171dcaeb21d4786808de6180d7218f2af');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    names={'AsyncJobMetricRecorderTest':'asyncGauge007ParallelSnapshotsRemainCompleteWithoutCrossOwnerOrSeriesGrowth','OutboxRowsMetricRecorderTest':'outboxMetric006ParallelSnapshotsRemainCompleteAndImmutable','OutboxAgeMetricRecorderTest':'outboxAge006OneOwnerPublishesWholeImmutableSnapshotsConcurrently'}
    for path,node in actual:
        identity=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==point);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);thread=a['rule']=='DoNotUseThreads';async_job='AsyncJob' in path
        assert name==names[Path(path).stem] and 'Executors.newFixedThreadPool(8)' in compact
        assert ('.range(0,64)' in compact and 'pool.invokeAll(jobs)' in compact) if async_job else ('i<64' in compact and 'executor.invokeAll(tasks)' in compact)
        assert ('returnread==first||read==second;' if async_job else 'returnactual==one||actual==two;') in compact
        if thread:
            reason='J2EE thread prohibition does not apply to the dedicated JavaSE JUnit fixture. An own eight-worker TWR executes exactly64 finite AtomicReference publication/read callbacks, no external waits or IO. invokeAll completes all Futures before get, caller registry is TWR and current007/006 passes within JVM240s. This is not an application executor or runtime ownership claim.';kind='OWN_FINITE64_ATOMIC_PUBLICATION'
        else:
            assert a['rule']=='CompareObjectsWithEquals'
            reason='Intentional exact supplied-snapshot identity oracle: every atomic publication/read must return one of the two original immutable input objects, not an equal newly allocated replacement. Value equality would weaken that current contract for record Counts/Ages; the normal snapshots themselves retain their independent values. The exact six == source points are test-only identity checks, not business value comparisons, and current007/006 passes.';kind='REQUIRED_EXACT_SUPPLIED_SNAPSHOT_IDENTITY'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[point:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==12 and sum(r['newSourceReason'] for r in rows)==6
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=12,existingThreadReferencesReauthenticated=6,newIdentitySourceReasons=6,rawRetained=12,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
