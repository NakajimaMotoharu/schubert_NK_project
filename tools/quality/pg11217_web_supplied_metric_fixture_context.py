"""Fourteen exact supplied metric JUnit/oracle contexts; no warning suppression or product replay."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11217-web-supplied-metric-fixture-context-v1'
POST=data.BASE/'PG11219-web-supplied-metric-fixture-context-post-v1'
SOURCE='ae55baa85af2174fa01d73b62ad8899d3f44f306'


def inputs():
    normal=data.read_checked(data.BASE/'PG11210-web-supplied-metric-fixture-six-compile-v1/manifest.json','11fb92b0b53b9dba26b93c8aa3e08c09c6c754b1b43fca1c20767ac270666d73')
    sp=data.BASE/'PG11214-web-supplied-metric-fixture-static-v1/manifest.json'
    static=data.read_checked(sp,STATIC_PIN)
    inverse=data.read_checked(data.BASE/'PG11208-web-supplied-metric-fixture-source-post-v1/manifest.json','a81a82ffb9963256e0ef7afa8213c3b4e4df8ae97aaec93bcafa30ffdef26820')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(sp.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==14
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    rule=node.get('rule')
    if rule=='EqualsNull':
        if stem=='WebDbPoolMetricRecorderTest':
            assert node.get('method').startswith('webPoolMetric002') and 'assertFalse(counts.equals(null));' in compact
            value='Counts'
        else:
            assert stem=='WebOutboxMetricRecorderTest' and node.get('method').startswith('webObxMet006')
            assert 'assertFalse(a.equals(null));' in compact
            value='Observation'
        return dict(kind='INDEPENDENT_RECORD_EQUALS_NULL_FALSE_CONTRACT',recordType=value,
            ownership='Direct equals(null) is the generated record contract under test, not a null-check of the receiver; changing to ==null would remove that assertion')
    if rule=='CompareObjectsWithEquals':
        assert stem=='WebDbPoolMetricRecorderTest' and node.get('method').startswith('webPoolMetric006')
        assert 'returnactual==first||actual==second;' in compact
        return dict(kind='INDEPENDENT_ORIGINAL_IMMUTABLE_INSTANCE_IDENTITY_ORACLE',ownership='Expected original first/second object identity, not value equality of reconstructed copies')
    if rule=='NullAssignment':
        assert stem=='WebOutboxMetricRecorderTest' and node.get('method').startswith('webObxMet002')
        assert 'absent[field]=null;' in compact and 'newObservation(1,1,1,absent[0],absent[1],absent[2])' in compact
        return dict(kind='EXPLICIT_NULL_AGE_NEGATIVE_TEST_FIXTURE',ownership='Each of three constructor age positions independently missing; assertThrows requires rejection, no exception-to-success conversion')
    if rule=='UseConcurrentHashMap':
        assert stem=='MediaBytesMetricRecorderTest' and node.get('method').startswith('mediaByte007')
        assert 'Map<String,Long>expected=newHashMap<>();' in compact
        assert 'tasks.add(()->{recorder.record(type,mode,status,bytes);returnnull;});' in compact
        assert compact.index('expected.merge(')<compact.index('executor.invokeAll(tasks)')
        return dict(kind='CALLER_PRECOMPUTED_EXPECTED_BYTE_MAP_NOT_SHARED_WITH_WORKER',ownership='All expected merges before submission; worker captures recorder/type/mode/status/bytes only; caller reads after joins')
    assert rule=='DoNotUseThreads' and ('006' in node.get('method','') or '007' in node.get('method',''))
    assert 'Executors.newFixedThreadPool(8)' in compact and any(x in compact for x in ('i<64','i<=64','index<64'))
    assert 'try(' in compact and not any(x in text for x in ('ProcessBuilder','getConnection(','java.net.','@Before','@After','@TempDir'))
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=8,tasks=64,
        ownership='Owned TWR executor and memory-only registries; all futures joined, original inner deadlines where present, enclosing dedicated JVM240s')


def require(rows,original,hashes,actual):
    if len(rows)!=14 or len({r['id'] for r in rows})!=14:
        raise ValueError('fourteen unique exact current contexts required')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('exact original occurrence/current coordinates required')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact source and concrete oracle/owner context required')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('no warning suppression or whole-current exemption')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('review is not product execution/coverage')


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
        reviewed=14,unclassifiedOriginalIds=[],rawWarnings=14,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        ('productTestsExecuted',32),('coverage',100),('oldRuntimeReassigned',True)]:
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=14,unclassified=0,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


STATIC_PIN='e5d43bcb6925b46f46ba1f408e7d80614231f576e058fe994e702beedbe98030'
PRIMARY_SHA=None

if __name__=='__main__':
    main()
