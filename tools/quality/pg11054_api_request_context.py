"""Sixteen exact API request static contexts; seventeenth shared field remains unclassified."""
from collections import Counter
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10910_current_f03_web_metric_delta import attrs

SOURCE = '9b255cbe300d1feffeeee076cfa5af318c9b1bb1'
OUT = data.BASE/'PG11054-api-request-context-v1'
POST = data.BASE/'PG11056-api-request-context-post-v1'
STATIC = data.BASE/'PG11040-api-request-static-v1'


def inputs():
    normal = data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
    static = data.read_checked(STATIC/'manifest.json','56546bff6f2b5922c20024bb24354ab54f79ad45d58a69b95b3ce320dd778d9e')
    proof = data.read_checked(data.BASE/'PG11044-api-request-post-v1/manifest.json','5a6444609c3ce10bc16a40cb024b2b02510cb9b6fae3e96087edf4b37c052c4a')
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert normal['source'] == static['source'] == proof['source'] == SOURCE and proof['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    raw = (STATIC/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd']['sha256']
    return normal,original,[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw)
        if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']


def reviewed_basis(path,node):
    text = (data.ROOT/path).read_text()
    compact = re.sub(r'\s+','',text)
    rule = node.get('rule')
    if rule == 'AvoidFieldNameMatchingMethodName':
        assert Path(path).stem == 'QuestionQueryRequestTest' and 'Field MESSAGE has the same name as a method' in (node.text or '')
        return None
    if rule == 'CloseResource' and 'Connection object' in (node.text or ''):
        assert Path(path).stem in ('ScenarioRequestTest','MediaRequestTest')
        assert 'Proxy.newProxyInstance(Connection.class.getClassLoader(),newClass<?>[]{Connection.class},' in compact
        assert 'thrownewAssertionError("null' in compact
        assert not any(s in text for s in ('getConnection(','DriverManager','DataSource'))
        main = path.replace('/test/','/main/').replace('RequestTest.java','Request.java')
        body = (data.ROOT/main).read_text()
        guards = 'Objects.requireNonNull(repository, "repository");\n    Objects.requireNonNull(connection, "connection");\n    Objects.requireNonNull(actor, "actor");'
        assert guards in body and len(re.findall(r'request\.query\(',text)) == 3
        return dict(kind='THROW_ONLY_JDBC_INTERFACE_PROXY_NO_ACQUIRED_RESOURCE',mainPath=main,mainSha256=data.sha(body.encode()),
            ownership='No JDBC connection acquired; every proxy method including close throws; all query calls fail one required null before dispatch')
    if rule == 'CloseResource':
        assert 'CanonicalField object' in (node.text or '') and 'canonical.fields()' in text
        assert re.search(r'try\s*\((?:var canonical =|canonical;|canonical\))',text)
        assert not any(s in text for s in ('new CanonicalField(','.fields().clear(','canonical = null'))
        return dict(kind='BORROWED_FIELD_ALIAS_CLOSED_BY_CANONICAL_OWNER',ownership='CanonicalRequest owns immutable field list; enclosing TWR closes every field; alias is not separately acquired')
    if rule == 'UseProperClassLoader':
        assert 'Connection.class.getClassLoader()' in text and 'Proxy.newProxyInstance(' in text
        return dict(kind='JDK_INTERFACE_PROXY_ORDINARY_JUNIT_NOT_J2EE',ownership='Use defining loader of exact public Connection interface in isolated host JUnit; no application context loader or server')
    assert Path(path).stem == 'QuestionSubmitRequestTest'
    assert 'try(varexecutor=Executors.newFixedThreadPool(8))' in compact
    assert 'i<64' in compact and '.get(5,TimeUnit.SECONDS)' in compact and '.get(10,TimeUnit.SECONDS)' in compact
    if rule == 'DoNotUseThreads':
        return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=8,tasks=64,
            ownership='Owned executor TWR; Future5/10 seconds; target JVM240 seconds; pure isolated in-memory requests only')
    assert rule == 'AvoidSynchronizedStatement' and 'synchronized(shared)' in compact
    assert 'executor.submit(()->newString(shared.copyQuestion())).get(5,TimeUnit.SECONDS)' in compact
    main = data.ROOT/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmitRequest.java'
    body = main.read_text()
    assert 'private final java.util.concurrent.locks.ReentrantLock stateLock' in body and 'synchronized' not in body
    return dict(kind='PUBLIC_MONITOR_INDEPENDENCE_ORACLE_FOR_PRIVATE_STATE_LOCK',mainSha256=data.sha(body.encode()),
        ownership='Holding public monitor while another thread copies must complete; replacing monitor with private test lock would remove this contract test')


def contract(rows,original,hashes,actual):
    if len(rows)!=16 or len({r['id'] for r in rows})!=16:
        raise ValueError('sixteen unique exact local contexts')
    allowed = {'CloseResource':{'BORROWED_FIELD_ALIAS_CLOSED_BY_CANONICAL_OWNER','THROW_ONLY_JDBC_INTERFACE_PROXY_NO_ACQUIRED_RESOURCE'},
        'UseProperClassLoader':{'JDK_INTERFACE_PROXY_ORDINARY_JUNIT_NOT_J2EE'},
        'DoNotUseThreads':{'FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME'},
        'AvoidSynchronizedStatement':{'PUBLIC_MONITOR_INDEPENDENCE_ORACLE_FOR_PRIVATE_STATE_LOCK'}}
    for row in rows:
        old = original[row['id']]
        if row['path']!=old['path'] or row['rule']!=old['rule'] or row['originalRowSha256']!=old['rowSha256']:
            raise ValueError('immutable original finding required')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or (row['path'],row['attributes']) not in actual:
            raise ValueError('exact current source and actual XML coordinates')
        if row['basis']['kind'] not in allowed.get(row['rule'],set()):
            raise ValueError('specific applicability basis, no shared-field exemption')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('raw retained; full-current execution not exempt')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('review not actual PT or coverage')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,original,actual = inputs()
    owner = data.ROOT/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/CanonicalRequest.java'
    assert 'fields = List.copyOf(fields);' in owner.read_text() and 'fields.forEach(CanonicalField::close);' in owner.read_text()
    inverse = data.read_checked(data.BASE/'PG11036-api-request-source-post-v1/manifest.json','d522060949a1716b4427dd13a43dc53ce5e0cf5f1e4e3d111fc1c52fd5e9091a')
    assert inverse['allOriginalOracleTokensRestored'] and inverse['metadataNegativeVectors']==14
    rows,unclassified = [],[]
    for path,node in actual:
        old = original_match(path,node,original,actual)
        basis=reviewed_basis(path,node)
        if basis is None:
            unclassified.append(old['id'])
            continue
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=basis,status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    assert len(unclassified)==1 and Counter(r['rule'] for r in rows)==Counter(CloseResource=8,DoNotUseThreads=5,UseProperClassLoader=2,AvoidSynchronizedStatement=1)
    contract(rows,{r['id']:r for r in original},normal['begin']['inputHashes'],[(p,dict(n.attrib)) for p,n in actual])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=16,unclassifiedOriginalIds=unclassified,rawWarnings=17,rawStaticGate=1,canonicalOwnerSha256=data.sha(owner.read_bytes()),
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def original_match(path,node,original,actual):
    def signature(rule,attributes,message):
        return rule,attrs(attributes),' '.join(message.split())
    key=signature(node.get('rule'),node.attrib,node.text or '')
    candidates=sorted([r for r in original if r['path']==path and signature(r['rule'],r['attributes'],r['message'])==key],
        key=lambda r:(int(r['attributes']['beginline']),int(r['attributes']['begincolumn'])))
    current=sorted([n for p,n in actual if p==path and signature(n.get('rule'),n.attrib,n.text or '')==key],
        key=lambda n:(int(n.get('beginline')),int(n.get('begincolumn'))))
    if not candidates or len(candidates)!=len(current) or len({(n.get('beginline'),n.get('begincolumn')) for n in current})!=len(current):
        raise ValueError('same-count preserved occurrence groups required')
    return candidates[current.index(node)]


def post():
    invocation=capture(Path(__file__))
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256'])
    normal,original,actual=inputs()
    args=({r['id']:r for r in original},normal['begin']['inputHashes'],[(p,dict(n.attrib)) for p,n in actual])
    contract(rows,*args)
    for row in rows:
        node=next(n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes'])
        assert reviewed_basis(row['path'],node)==row['basis']
    bads=[rows[:-1],rows+[rows[0]]]
    for field,value in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),
        ('ptExecutionExempt',True),('productTestsExecuted',16),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][field]=value
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,*args)
        except ValueError:
            pass
        else:
            raise AssertionError('invented current source/coverage/acceptance')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=16,unclassified=1,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA = None

if __name__ == '__main__':
    main()
