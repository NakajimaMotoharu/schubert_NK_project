"""Twelve current standalone JDBC fixture J2EE applicability points, all prior references rebound."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='21daf2722f9b280ec005b1b971300774a1d3716f'
OUT=data.BASE/'PG11771-jdbc-collector-owner-context-v1'

def review():
    host=data.read_checked(data.BASE/'PG11766-jdbc-collector-literal-host-v1/manifest.json','d5565981b616135c0d08d6cc686245143ad405c89c0cb020ba834101bba2ed0d');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==16
    eligibility=host['begin']['eligibilityClosureSourceHashes'];assert len(eligibility)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in eligibility.items())
    sp=data.BASE/'PG11768-jdbc-collector-literal-static-v1';st=data.read_checked(sp/'manifest.json','1fb16cae2dcaf613917f2a8bd4abce746130911ecf3525ab45b66c00748b3c68');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==point);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);loader=a['rule']=='UseProperClassLoader';async_job='AsyncJob' in path;prefix='asyncConn' if async_job else 'outboxConn'
        if loader:
            assert name=='gate' and 'Proxy.newProxyInstance(Connection.class.getClassLoader(),newClass<?>[]{Connection.class},' in compact
            assert 'release.await(5,TimeUnit.SECONDS)' in compact
            method=next(c['method'] for c in host['begin']['cases'] if c['path']==path and c['method'].startswith(prefix+'006'))
            kind='DECLARING_JDBC_INTERFACE_LOADER';reason='The J2EE context-loader rule does not apply to this dedicated JavaSE JUnit double. Its exact java.sql.Connection declaring-interface loader creates a Proxy implementing only that interface. The reviewed handler permits only borrowed readonly getters/prepare and rejects all other operations; the delegate is the strict memory Fixture, not a Driver/DataSource. Current006 uses this helper and passes. No arbitrary class loading, server authority or Graph9 classifier is involved.'
        else:
            assert a['rule']=='DoNotUseThreads' and name.startswith((prefix+'006',prefix+'007'));method=name
            if name.startswith(prefix+'006'):
                assert 'Executors.newFixedThreadPool(2)' in compact and compact.count('pool.submit(')==2 and 'finally{release.countDown();}' in compact and 'one.get(5,TimeUnit.SECONDS)' in compact and 'two.get(5,TimeUnit.SECONDS)' in compact
                kind='OWN_GATED_TWO_TASKS';reason='J2EE thread prohibition is not applicable to the standalone fixture. It owns two TWR workers and strict memory JDBC delegates, gate/latch/get deadlines5s and a finally release before executor close. Current006 checks no second entry during the original100ms observation and successful serialized outcomes; this bounded observation is not proof of every scheduling history. No actual DB, service or external lock/Root is used.'
            else:
                assert 'Executors.newFixedThreadPool(8)' in compact and 'pool.invokeAll(tasks)' in compact and ('owner<64' if async_job else 'owner<=64') in compact
                kind='OWN_FINITE64_READS';reason='J2EE thread prohibition is not applicable to the standalone fixture. Its own eight-worker TWR executes exactly64 finite strict Proxy reads and local SDK publications for the caller-owned collector; invokeAll completes all Futures before get. Current007 checks independent rows/owner counts and registry shape. Query-timeout values are asserted by a double, not a real DB deadline; whole JVM240s guard and no actual IO/Graph9 closure are retained.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==method);assert any(c['classname']==case['className'] and c['name']==method and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[point:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==12 and sum(r['rule']=='UseProperClassLoader' for r in rows)==2
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=12,existingThreadReferencesReauthenticated=10,existingLoaderReferencesReauthenticated=2,newSourceReasons=0,rawRetained=12,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
