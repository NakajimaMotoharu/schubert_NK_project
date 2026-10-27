"""Six exact ordinary HTTP recorder JUnit loader/thread/caller-map contexts; retain raw warnings."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11271-http-recorder-fixture-context-v1'
POST=data.BASE/'PG11273-http-recorder-fixture-context-post-v1'
SOURCE='064294de0f47e195a99e5fab76e2fe92ea31256d'


def inputs():
    normal=data.read_checked(data.BASE/'PG11264-http-recorder-fixture-six-compile-v1/manifest.json',
        '87b29c22a2f3b612936173d8633cd67201368bc1f711938a0f1e834624f17d9f')
    static_path=data.BASE/'PG11268-http-recorder-fixture-static-v1/manifest.json'
    static=data.read_checked(static_path,'def0cf0a74811d7de0e2c38f64f96932b0abb71fe44fef5388ee36ac88516c7a')
    inverse=data.read_checked(data.BASE/'PG11262-http-recorder-fixture-source-post-v1/manifest.json',
        '9d26ac92cb98432c5e40c91eb4c9f74b1a6b63aa173f616f85db8b35b4bb0923')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==6 and static['actualExit']==1
    return normal,original,actual


def basis(path,node):
    assert path.endswith('/HttpMetricRecorderTest.java')
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    rule=node.get('rule')
    if rule=='UseProperClassLoader':
        assert node.get('method')=='newTimer' and 'Proxy.newProxyInstance(Timer.class.getClassLoader(),newClass<?>[]{Timer.class}' in compact
        assert not any(x in text for x in ('setAccessible','Class.forName','URLClassLoader','defineClass'))
        return dict(kind='EXACT_TIMER_INTERFACE_LOADER_FOR_OWN_MEMORY_PROXY_NOT_J2EE',
            ownership='Only fixed Timer interface and owned delegate; no context loader substitution, arbitrary class path or access change')
    if rule=='UseConcurrentHashMap':
        assert node.get('method')=='httpRec010ExtremeRangeOrdersNeverWrapCumulativeTimerOrLoseSmallBuckets'
        assert 'Map<Double,Double>counts=newHashMap<>();' in compact and 'counts.put(bucket.bucket(),bucket.count());' in compact
        assert 'for(varbucket:metric.takeSnapshot().histogramCounts())' in compact
        return dict(kind='CALLER_ONLY_ACTUAL_SNAPSHOT_COLLECTION_NOT_SHARED_WITH_WORKERS',
            ownership='Local per fixed input order; independent literal SS key set and CDF3 expected, no worker captures map')
    assert rule=='DoNotUseThreads' and node.get('method')=='httpRec007ConcurrentActualProviderCounts'
    assert 'try(varexecutor=Executors.newFixedThreadPool(4))' in compact and 'index<64' in compact
    assert 'executor.invokeAll(tasks,10,TimeUnit.SECONDS)' in compact and 'executor.shutdownNow();' in compact
    assert 'assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS));' in compact
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=4,tasks=64,
        ownership='Original future10s plus finally shutdownNow/await10s preserved; outer TWR owner close; enclosing dedicated JVM240s')


def require(rows,original,hashes,actual):
    if len(rows)!=6 or len({r['id'] for r in rows})!=6:
        raise ValueError('six unique actual context bindings')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('original warning ID and current exact coordinates')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact source and concrete ownership context')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('retain raw and whole qualification pending')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('context metadata not execution/coverage')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs()
    rows=[]
    for path,node in actual:
        old=original_match(path,node,original,actual)
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=basis(path,node),
            status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',rawWarningRetained=True,ptExecutionExempt=False,
            productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,original,normal['begin']['inputHashes'],actual)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=6,unclassifiedOriginalIds=[],rawWarnings=6,rawStaticGate=1,productTestsExecuted=0,coverage=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256'])
    normal,original,actual=inputs()
    require(rows,original,normal['begin']['inputHashes'],actual)
    bads=[rows[:-1],rows+[rows[0]]]
    for k,v in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),('ptExecutionExempt',True),
        ('productTestsExecuted',10),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][k]=v
        bads.append(bad)
    for bad in bads:
        try:
            require(bad,original,normal['begin']['inputHashes'],actual)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid context/runtime metadata accepted')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=6,unclassified=0,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()
