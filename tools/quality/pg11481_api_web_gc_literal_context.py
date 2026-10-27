"""Current24 GC fixture contexts; preserve four new-method diagnostic IDs from the original registry."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11054_api_request_context import attrs,original_match
from pg11451_gc_fake_guard_context_v3 import basis

SOURCE='d1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7'
OUT=data.BASE/'PG11481-api-web-gc-literal-context-v1'
POST=data.BASE/'PG11483-api-web-gc-literal-context-post-v1'
PRIMARY_SHA=None

def inputs():
    normal=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    path=data.BASE/'PG11478-api-web-gc-literal-static-v1/manifest.json'
    static=data.read_checked(path,'1a50d80fd30b1809f89a55e0bab3d9b51100f9e89251970d71bdd78aab5a05bd')
    inverse=data.read_checked(data.BASE/'PG11472-api-web-gc-literal-source-post-v1/manifest.json','f307c042461dad4bc34301cc7dd5514c78c36c27cc5ad7114b0c202051a6ac3b')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(path.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    prior=data.read_checked(data.BASE/'PG11451-gc-fake-guard-context-v3/manifest.json','6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb')
    discoveries=data.read_checked(data.BASE/'PG11451-gc-fake-guard-context-v3/new-diagnostics.json',prior['newDiagnosticsSha256'])
    assert len(actual)==24
    return normal,original,actual,discoveries

def identity(path,node,original,actual,discoveries):
    matches=[r for r in discoveries if r['path']==path and attrs(r['attributes'])==attrs(node.attrib) and r['descriptor']['message']==''.join(node.itertext()).strip()]
    if matches:
        assert len(matches)==1
        return matches[0]
    return original_match(path,node,original,actual)

def require(rows,normal,original,actual,discoveries):
    if len(rows)!=24 or len({r['id'] for r in rows})!=24:
        raise ValueError('all24 actual distinct contexts')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or identity(row['path'],node,original,actual,discoveries)['id']!=row['id']:
            raise ValueError('exact original or retained new-method diagnostic identity')
        if row['source']!=SOURCE or row['sourceSha256']!=normal['begin']['inputHashes'][row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact current source and fixture-specific cleanup context')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt'] or row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('no exemption, suppression, invented PT or coverage')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal,original,actual,discoveries=inputs();rows=[]
    for path,node in actual:
        old=identity(path,node,original,actual,discoveries)
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],attributes=dict(node.attrib),
            identityRowSha256=old['rowSha256'],basis=basis(path,node),status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',rawWarningRetained=True,
            ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,normal,original,actual,discoveries)
    retained=sorted(r['id'] for r in rows if r['id'].startswith('PMD-NEW-'))
    assert retained==['PMD-NEW-PG11448-001','PMD-NEW-PG11448-002','PMD-NEW-PG11448-005','PMD-NEW-PG11448-006']
    verify(invocation);OUT.mkdir();data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=24,unclassifiedOriginalIds=[],retainedNewDiagnosticIds=retained,newDiagnosticIdsAdded=0,rawWarnings=24,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256'])
    args=inputs();require(rows,*args)
    bads=[rows[:-1],rows+[rows[0]]]
    for key,value in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),('ptExecutionExempt',True),('productTestsExecuted',32),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows);bad[0][key]=value;bads.append(bad)
    bad=copy.deepcopy(rows);next(r for r in bad if r['id'].startswith('PMD-NEW-'))['id']='PMD-00001';bads.append(bad)
    for bad in bads:
        try:
            require(bad,*args)
        except ValueError:
            pass
        else:
            raise AssertionError('wrong or reassigned source/diagnostic/runtime accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=24,unclassified=0,
        retainedNewDiagnosticIds=primary['retainedNewDiagnosticIds'],newDiagnosticIdsAdded=0,rawStaticGate=1,productTestsExecuted=0,coverage=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
