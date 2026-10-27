"""Six finite JUnit worker and two caller-only expected Map contexts; one Comparable warning unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11245-batch-supplied-metric-label-fixture-context-v1'
POST=data.BASE/'PG11247-batch-supplied-metric-label-fixture-context-post-v1'
SOURCE='ef86a244b2f528a2d60bd0f22a94a853ce3146ff'


def inputs():
    normal=data.read_checked(data.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1/manifest.json','5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe')
    static_path=data.BASE/'PG11242-batch-supplied-metric-label-fixture-static-v1/manifest.json'
    static=data.read_checked(static_path,'daf9fa3dd62ebebe03884b3e729628f74672e212a6873ce63ddef0ffb8a397f2')
    proof=data.read_checked(data.BASE/'PG11244-batch-supplied-metric-label-fixture-post-v1/manifest.json','bbe1078458fcab7da33b9a541290b4b2fcf21d9017a681c00e83471d25e61aee')
    inverse=data.read_checked(data.BASE/'PG11236-batch-supplied-metric-label-fixture-source-post-v1/manifest.json','2af153d43b00260ce35d96aef97d796f5c8b366c9e015af82c5017a62f8e68fa')
    assert normal['source']==static['source']==proof['source']==SOURCE and proof['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==9
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    rule=node.get('rule')
    if rule=='OverrideBothEqualsAndHashCodeOnComparable':
        assert stem=='BatchMetricLabelPolicyTest' and node.get('method')=='compareTo'
        return None
    if rule=='UseConcurrentHashMap':
        assert stem in ('ProcessRestartMetricRecorderTest','IntegrityFailureMetricRecorderTest') and '007' in node.get('method','')
        assert 'Map<String,Integer>expected=newHashMap<>();' in compact
        call='reason,service' if stem=='ProcessRestartMetricRecorderTest' else 'area,step'
        assert 'tasks.add(()->{recorder.record('+call+');returnnull;});' in compact
        assert compact.index('expected.merge(')<compact.index('executor.invokeAll(tasks)')
        return dict(kind='CALLER_PRECOMPUTED_EXPECTED_MAP_NOT_SHARED_WITH_WORKERS',ownership='All expected increments before submission; workers capture recorder and typed input enums only; caller reads after joins')
    assert rule=='DoNotUseThreads' and 'i<64' in compact
    workers=4 if stem=='BatchMetricLabelPolicyTest' else 8
    assert 'Executors.newFixedThreadPool('+str(workers)+')' in compact and 'try(' in compact
    assert not any(x in text for x in ('ProcessBuilder','getConnection(','java.net.','@Before','@After','@TempDir'))
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=workers,tasks=64,
        ownership='Owned TWR executor/registries, pure supplied event enums or fixed labels; joined original5/10s futures and enclosing dedicated JVM240s')


def require(rows,original,hashes,actual):
    if len(rows)!=8 or len({r['id'] for r in rows})!=8:
        raise ValueError('eight unique concrete current contexts required')
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
    assert len(unclassified)==1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=8,unclassifiedOriginalIds=unclassified,rawWarnings=9,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=8,unclassified=1,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

