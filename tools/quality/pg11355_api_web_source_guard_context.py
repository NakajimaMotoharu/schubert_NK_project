"""Twelve exact API/Web source owner JUnit contexts;four composite GC warnings remain unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11355-api-web-source-guard-context-v1'
POST=data.BASE/'PG11357-api-web-source-guard-context-post-v1'
SOURCE='d4b5507ba6a76a85c23806e5604a0278f1795f37'


def inputs():
    normal=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json','46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    static_path=data.BASE/'PG11352-api-web-source-guard-static-v1/manifest.json'
    static=data.read_checked(static_path,'aac5877aeea4e595f71d3e7fb1e823c07490938011be0c7f2d5c6dc716794ddc')
    inverse=data.read_checked(data.BASE/'PG11346-api-web-source-guard-source-post-v1/manifest.json','6391ecbb2007f1f57a53476e9bc004a3864a3067c21a17fca812399719c171b6')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==16
    return normal,original,actual


def basis(path,node):
    assert Path(path).stem in ('ApiStandardMetricSourceTest','WebStandardMetricSourceTest')
    prefix = 'apihost' if Path(path).stem.startswith('Api') else 'webhost'
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    if node.get('rule')=='CloseResource':
        assert node.get('variable')=='gc' and node.get('method') in (prefix+'011GcRetainedBeforeFatalAndClosedInReverseOrder',prefix+'012FailedGcCloseKeepsRegistryAndExplicitRetryOwnership')
        return None
    assert node.get('rule')=='DoNotUseThreads'
    assert node.get('method') in (prefix+'016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes','scrape')
    assert 'try(varexecutor=Executors.newFixedThreadPool(2))' in compact
    assert 'release.countDown();executor.shutdownNow();assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS));owner.close();' in compact
    assert 'Thread.currentThread().interrupt();' in compact and 'await(10,TimeUnit.SECONDS)' in compact
    assert compact.count('finally{owner.close();}')==15
    return dict(kind='FINITE_ORDINARY_JUNIT_OWN_LATCH_SCRAPE_CLOSE_INTERRUPT_RESTORATION',workers=2,tasks=2,
        ownership='Only own ProbeRegistry/owner, original latches/joins10s and release/shutdown/await retained; owner guarded from declaration, executor TWR; enclosing JVM240s')

def require(rows,original,hashes,actual):
    if len(rows)!=12 or len({r['id'] for r in rows})!=12:
        raise ValueError('twelve unique concrete current contexts required')
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
    assert len(unclassified)==4
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=12,unclassifiedOriginalIds=unclassified,rawWarnings=16,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=12,unclassified=4,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

