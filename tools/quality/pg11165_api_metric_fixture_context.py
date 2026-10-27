"""Twelve exact ordinary-JUnit worker/main-thread-map contexts; retain raw warnings."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11165-api-metric-fixture-context-v1'
POST=data.BASE/'PG11167-api-metric-fixture-context-post-v1'
SOURCE='aafcc38d2d48627e10f816dd45bfaeb20bf5e415'


def inputs():
    normal=data.read_checked(data.BASE/'PG11158-api-metric-fixture-six-compile-v1/manifest.json','580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c')
    sp=data.BASE/'PG11162-api-metric-fixture-static-v1/manifest.json'
    static=data.read_checked(sp,'d5e5db629b48946657e44567fbfc37c2281ff19a8af5d3a879809b0bc89d7177')
    inverse=data.read_checked(data.BASE/'PG11156-api-metric-fixture-source-post-v1/manifest.json','a7ca42f4610d8d066afaa7696098f528fa3d2d95fe1e2ce4675fb90607d4376a')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(sp.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==12
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    if node.get('rule')=='UseConcurrentHashMap':
        assert stem=='DbQueryDurationMetricRecorderTest'
        if node.get('method').startswith('dbTime002'):
            assert 'Map<Double,Double>counts=newHashMap<>();for(varbucket:value.takeSnapshot().histogramCounts())counts.put(bucket.bucket(),bucket.count());' in compact
            return dict(kind='METHOD_LOCAL_CDF_COPY_ONLY_JUNIT_CALLER_THREAD',ownership='Snapshot bucket counts copied and asserted sequentially; object neither returned nor captured by worker')
        assert node.get('method').startswith('dbTime007')
        assert all('Map<String,Long>'+name+'=newHashMap<>();' in compact for name in ('counts','sums','maxima'))
        assert 'tasks.add(()->{recorder.record(query,outcome,ns);returnnull;});' in compact
        assert compact.index('counts.merge(key,1L,Long::sum);')<compact.index('executor.invokeAll(tasks)')
        assert compact.index('sums.merge(key,ns,Long::sum);')<compact.index('executor.invokeAll(tasks)')
        assert compact.index('maxima.merge(key,ns,Long::max);')<compact.index('executor.invokeAll(tasks)')
        return dict(kind='CALLER_PRECOMPUTED_EXPECTED_MAP_NOT_CAPTURED_OR_MUTATED_BY_WORKERS',ownership='All merges precede task submission; worker captures recorder/query/outcome/ns only; caller reads after futures')
    assert node.get('rule')=='DoNotUseThreads' and node.get('method') and '007' in node.get('method')
    assert 'Executors.newFixedThreadPool(8)' in compact and ('i<64' in compact or 'index<64' in compact)
    assert 'try(' in compact and not any(x in text for x in ('ProcessBuilder','getConnection(','java.net.','@Before','@After','@TempDir'))
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=8,tasks=64,
        ownership='Owned TWR executor and in-memory SDK registries; all tasks joined; original inner deadlines where present, enclosing dedicated JVM240s')


def require(rows,original,hashes,actual):
    if len(rows)!=12 or len({r['id'] for r in rows})!=12:
        raise ValueError('twelve unique exact contexts required')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('exact original occurrence/current coordinates required')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('source and concrete nonshared-map/finite-worker context required')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('no raw suppression or whole-current exemption')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('review is not execution/coverage')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs()
    rows=[]
    for path,node in actual:
        old=original_match(path,node,original,actual)
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=basis(path,node),status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,original,normal['begin']['inputHashes'],actual)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=12,unclassifiedOriginalIds=[],rawWarnings=12,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        ('productTestsExecuted',34),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][k]=v
        bads.append(bad)
    for bad in bads:
        try:
            require(bad,original,normal['begin']['inputHashes'],actual)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid context metadata accepted')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=12,unclassified=0,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()
