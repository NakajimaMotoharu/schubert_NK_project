"""Six finite JUnit worker and two reference identity contexts; two Tag Comparable warnings unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11191-api-catalog-scalar-pool-context-v1'
POST=data.BASE/'PG11193-api-catalog-scalar-pool-context-post-v1'
SOURCE='5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81'


def inputs():
    normal=data.read_checked(data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json','b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b')
    static_path=data.BASE/'PG11188-api-catalog-scalar-pool-static-v1/manifest.json'
    static=data.read_checked(static_path,'971a69f774393a5e92325bd23ca52880338ef31e7828c8b64f9b53e474bc61b9')
    proof=data.read_checked(data.BASE/'PG11190-api-catalog-scalar-pool-post-v1/manifest.json','f391e0c02c03d0b716e9f47a13d4cb4acb2bf00df67f5db6ad781cf2e33af8a7')
    inverse=data.read_checked(data.BASE/'PG11182-api-catalog-scalar-pool-source-post-v1/manifest.json','c49c95c433cbd6ea2cb1ae67e45341b3de9483dcf63d75b3a4ac525421c42e0c')
    assert normal['source']==static['source']==proof['source']==SOURCE and proof['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==10
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    rule=node.get('rule')
    if rule=='OverrideBothEqualsAndHashCodeOnComparable':
        assert stem in ('ApiMetricCatalogTest','ApiScalarMetricExporterTest') and node.get('method')=='compareTo'
        return None
    if rule=='CompareObjectsWithEquals':
        assert stem=='DbPoolMetricRecorderTest' and node.get('method')=='poolMetric006ParallelUpdatesKeepWholeImmutableSnapshots'
        assert 'returnactual==first||actual==second;' in compact
        return dict(kind='INDEPENDENT_REFERENCE_IDENTITY_ORACLE_NOT_VALUE_EQUALITY',ownership='Existing test requires one original immutable Counts instance, not a value-equal reconstructed copy; switching to equals would weaken the original assertion')
    assert rule=='DoNotUseThreads' and ('i<64' in compact or 'index<64' in compact)
    workers=8 if stem=='DbPoolMetricRecorderTest' else 4
    assert 'Executors.newFixedThreadPool('+str(workers)+')' in compact and 'try(' in compact
    assert not any(x in text for x in ('ProcessBuilder','getConnection(','java.net.','@Before','@After','@TempDir'))
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=workers,tasks=64,
        ownership='Owned TWR executor/registries and memory-only writer; all futures joined; existing inner10s where present, enclosing dedicated JVM240s')


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
    assert len(unclassified)==2
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=8,unclassifiedOriginalIds=unclassified,rawWarnings=10,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=8,unclassified=2,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

