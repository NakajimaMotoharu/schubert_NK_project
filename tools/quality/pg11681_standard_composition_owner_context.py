"""Eight exact current source owner/thread points; no test execution or old runtime transfer."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='5a16139a752e2404cd6c26504760f4568ac413fd'
OUT=data.BASE/'PG11681-standard-composition-owner-context-v1'

def review():
    hp=data.BASE/'PG11676-standard-composition-literal-host-v1/manifest.json'
    host=data.read_checked(hp,'0b1d596e787572a815067ee1abaf91b5ef18f7b0c89a26c0a6fd58dfa46b570b')
    assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==26
    sp=data.BASE/'PG11678-standard-composition-literal-static-v1';st=data.read_checked(sp/'manifest.json','d8819401772f3a93f4ed5eceb2b2a7ceb7373583b393b74690f2ca1b6f5ae73e')
    raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        a=node.attrib;lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];index=next(i for i,(_,p) in enumerate(ts) if p==point)
        ma,mb,name=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1])
        worker=a['rule']=='DoNotUseThreads'
        if worker:
            assert name.endswith('013FiniteIndependentConcurrentCompositions')
            assert 'try(varworkers=Executors.newFixedThreadPool(4)){' in compact and 'i<64' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact
            assert 'assertEquals(192,total.get())' in compact and 'local.incrementAndGet();total.incrementAndGet();' in compact
            reason='J2EE thread prohibition does not apply to the dedicated JavaSE JUnit fixture. Its sole own four-worker TWR executes exactly64 finite recording/atomic tasks, each three fixed ports and no external waits; each Future is joined at10s, registry owned in each task, and the current original013 passes within the whole JVM240s boundary. No server executor or Root recovery is involved; whole-source applicability remains pending.'
        else:
            assert a['rule']=='CloseResource' and any(name.endswith(s) for s in ('006ClosedDebugFailsBeforeAnyPhase','011ClosedStandardDoesNotReadOrReclose'))
            assert 'varsource=newRegistry();source.close();' in compact and 'assertEquals(1,source.closes.get());' in compact
            assert compact.count('source.close();')==1
            reason='The fresh memory Registry is explicitly closed immediately before supplying the intentionally closed input to the SUT. The fixed oracle asserts one close and forbids implicit reclose; adding a second TWR close would change that oracle. No bind or GC resource is installed on this registry. The current original006/011 passes; raw warning retained with this exact required contract, not blanket suppression.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[point:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,disposition='CONTEXT_NOT_APPLICABLE' if worker else 'REQUIRED_CONTRACT',reason=reason,previousReferenceRetainedAsHistorical=worker,newSourceReason=not worker,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==8 and sum(r['newSourceReason'] for r in rows)==4
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=8,existingThreadReferencesReauthenticated=4,newClosedRegistryReasons=4,rawRetained=8,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
