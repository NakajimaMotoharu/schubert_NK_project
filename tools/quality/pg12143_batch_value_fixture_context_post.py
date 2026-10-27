"""Independent loader helper/source span and its two actual callers, ten metadata negatives."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='8a229695c0ea503ebac8761993665242eeba0107'
OUT=data.BASE/'PG12143-batch-value-fixture-context-post-v1'
PIN='f7de8c789c6e84d9663b892c5646561e981b3cdda626321565f45b994f684da6'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12141-batch-value-fixture-context-v1';m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12137-batch-value-fixture-host-v2/manifest.json','6d36cec96c35f98711f9f6e4ac9debe5e6f67160bb9a640e41c1a9209cb0ae67');sp=data.BASE/'PG12139-batch-value-fixture-static-v2';st=data.read_checked(sp/'manifest.json','5511be09a7cb8e0f986d5a510a428a93d0b66d8bad813bb75d5b7193513a6a18');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];assert len(actual)==len(rows)==1
    path,node=actual[0];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');ident=original_match(path,node,original,actual);a=dict(node.attrib);text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(v.group(),v.start()) for v in LEX.finditer(text) if not v.group().startswith(('//','/*'))];i=next(i for i,(_,pos) in enumerate(ts) if pos==start);methods=functions(ts);lo,hi,name=min((v for v in methods if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1])
    assert name=='unused' and 'ClientSession.class.getClassLoader()' in body and 'Proxy.newProxyInstance(' in body and 'thrownewAssertionError(' in body and 'newClass<?>[]{ClientSession.class}' in body
    expected_names=['brokerFieldsComeFromElevenReadsAndMutableDiskNumberIsCapturedOnce','queueCountAndBytesAreNotLostAndRemainIndependentOfLaterFixtureChanges'];callers=[]
    for method in expected_names:
        span=next(v for v in methods if v[2]==method);assert 'unused()' in ''.join(t for t,_ in ts[span[0]:span[1]+1]);case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==method);assert any(c['classname']==case['className'] and c['name']==method and not c['nonPass'] for c in host['cases']);callers.append(case)
    assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path] and host['source']==SOURCE and host['actualExit']==0
    expected=dict(id=ident['id'],path=path,rule='UseProperClassLoader',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method='unused',helperMethod='unused',methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=callers[0],associatedCurrentCases=callers,kind='BORROWED_INTERFACE_DEFINITION_LOADER',disposition='REQUIRED_CONTRACT',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
    def validate(row):
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact source/helper/span/interface loader/two current callers required')
    validate(rows[0]);negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('helperMethod','foreign'),('currentCase',{}),('associatedCurrentCases',[]),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('bad helper source/caller metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=1,existingLoaderReferencesReauthenticated=1,newSourceReasons=0,associatedActualCallers=2,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
