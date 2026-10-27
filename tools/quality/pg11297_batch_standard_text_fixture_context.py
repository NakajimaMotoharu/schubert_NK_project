"""Twenty exact Batch standard-to-text JUnit thread/null contexts;32 resource/Comparable warnings remain unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11297-batch-standard-text-fixture-context-v1'
POST=data.BASE/'PG11299-batch-standard-text-fixture-context-post-v1'
SOURCE='d431ad964355c4e5c602fcb94fe0182da6ae3a61'


def inputs():
    normal=data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json','e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
    static_path=data.BASE/'PG11294-batch-standard-text-fixture-static-v1/manifest.json'
    static=data.read_checked(static_path,'8ebe64d8773c98c27db1180a4187829280886700c487c6c96021bdec9807ab63')
    inverse=data.read_checked(data.BASE/'PG11288-batch-standard-text-fixture-source-post-v1/manifest.json','82120e6bf02d1d70a66f2c866e5d20c5afd2bb44bf7902d26afcb899cd5514ac')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==52
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    rule=node.get('rule')
    method=node.get('method')
    if rule in ('CloseResource','OverrideBothEqualsAndHashCodeOnComparable'):
        return None
    if rule=='NullAssignment':
        assert stem=='BatchMetricTextTest' and method=='batchtext009NullListMeterIdentityAndNameFail'
        assert 'source.meters=null;' in compact and 'assertThrows(NullPointerException.class,()->formatter.scrape(source,DEBUG_MODE));' in compact
        return dict(kind='EXPLICIT_NULL_LIST_NEGATIVE_INPUT_NOT_NORMAL_STATE',ownership='Owned Registry TWR; independent boundary rejection, no normal null state or NPE catch')
    assert rule=='DoNotUseThreads'
    if stem=='BatchStandardMetricSourceTest':
        assert method in ('batchhost016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes','scrape')
        assert 'release.countDown();executor.shutdownNow();assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS));owner.close();' in compact
        assert 'Thread.currentThread().interrupt();' in compact and 'await(10,TimeUnit.SECONDS)' in compact
        return dict(kind='FINITE_OWNER_LATCH_AND_INTERRUPT_RESTORATION_IN_ORDINARY_JUNIT',workers=2,tasks=2,
            ownership='Only owned ProbeRegistry/owner; latch and joins10s; finally release/shutdown/await/close; scrape restores interrupt and propagates fixed failure')
    if stem=='BatchMetricTextTest':
        assert method in ('batchtext024FiniteConcurrentCallsKeepBorrowedOwner','batchfull011ConcurrentBorrowedSourcesNeverMixOrClose')
        assert 'job.get(10,TimeUnit.SECONDS)' in compact and 'firstJob.get(10,TimeUnit.SECONDS)' in compact
        return dict(kind='FINITE_ORDINARY_JUNIT_BORROWED_TEXT_SOURCES_NOT_J2EE',
            workers=4 if method.startswith('batchtext024') else 2,tasks=64 if method.startswith('batchtext024') else 2,
            ownership='TWR workers and sources; fixed counter/text vectors; two fixed16-event probe-owner loops for full text; enclosing JVM240s')
    methods={'BatchJvmMetricsTest':'batchjvm014FiniteConcurrentPortsDoNotShareSourceState',
        'BatchSystemMetricsTest':'batchsys014FiniteConcurrentPortsDoNotShareSourceState',
        'BatchGcMetricRegistrationTest':'batchgc013FiniteIndependentConcurrentOwnerScopes',
        'BatchStandardMetricsTest':'batchstd013FiniteIndependentConcurrentCompositions'}
    assert stem in methods and method==methods[stem]
    assert 'try(varworkers=Executors.newFixedThreadPool(4))' in compact and 'i<64' in compact
    assert 'job.get(10,TimeUnit.SECONDS)' in compact and 'workers.submit(' in compact
    return dict(kind='FINITE_ORDINARY_JUNIT_FIXED_PORT_OR_FAKE_GC_NOT_J2EE',workers=4,tasks=64,
        ownership='Each worker owns isolated Registry and fixed callback counters; fake GC activation only; TWR/join10s/enclosingJVM240s, not application worker runtime')

def require(rows,original,hashes,actual):
    if len(rows)!=20 or len({r['id'] for r in rows})!=20:
        raise ValueError('twenty unique concrete current contexts required')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('original same-signature occurrence and actual coordinates')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact source and concrete owner/thread context')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('no suppression or whole-current exemption')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('static review is not execution/coverage')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs()
    rows,unclassified=[],[]
    for path,node in actual:
        old=original_match(path,node,original,actual)
        context=basis(path,node)
        if context is None:
            unclassified.append(old['id'])
            continue
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=context,status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,original,normal['begin']['inputHashes'],actual)
    assert len(unclassified)==32
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=20,unclassifiedOriginalIds=unclassified,rawWarnings=52,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        ('productTestsExecuted',24),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][k]=v
        bads.append(bad)
    for bad in bads:
        try:
            require(bad,original,normal['begin']['inputHashes'],actual)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/runtime/context metadata')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=20,unclassified=32,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

