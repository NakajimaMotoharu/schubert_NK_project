"""One exact borrowed-interface proxy loader helper bound to its two actual current callers."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='8a229695c0ea503ebac8761993665242eeba0107'
OUT=data.BASE/'PG12141-batch-value-fixture-context-v1'
def main():
    invocation=capture(__file__);assert not OUT.exists()
    host=data.read_checked(data.BASE/'PG12137-batch-value-fixture-host-v2/manifest.json','6d36cec96c35f98711f9f6e4ac9debe5e6f67160bb9a640e41c1a9209cb0ae67');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==4
    proof=data.read_checked(data.BASE/'PG12145-batch-value-fixture-post-v2/manifest.json','3ce8bd128c33539f9ef8eb6b953d37e550e54c64be6a7b98d914e460d6633de2');assert proof['actualExit']==0 and proof['artifactMeasurements']['batch']['operationIsolationInstructionsCovered']==0
    p=data.BASE/'PG12139-batch-value-fixture-static-v2';m=data.read_checked(p/'manifest.json','5511be09a7cb8e0f986d5a510a428a93d0b66d8bad813bb75d5b7193513a6a18');raw=(p/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];assert len(actual)==1
    path,node=actual[0];assert path=='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisDetailedValuesTest.java'
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');ident=original_match(path,node,original,actual);a=dict(node.attrib);assert a['rule']=='UseProperClassLoader'
    text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
    ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,pos) in enumerate(ts) if pos==start);all_methods=functions(ts);lo,hi,name=min((v for v in all_methods if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1]);assert name=='unused' and all(s in body for s in ('Proxy.newProxyInstance(ClientSession.class.getClassLoader(),','newClass<?>[]{ClientSession.class}','thrownewAssertionError('))
    callers=[]
    for case in host['begin']['cases']:
        if case['path']!=path:continue
        span=next(v for v in all_methods if v[2]==case['method']);compact=''.join(t for t,_ in ts[span[0]:span[1]+1])
        if 'unused()' in compact:
            assert any(c['classname']==case['className'] and c['name']==case['method'] and not c['nonPass'] for c in host['cases']);callers.append(case)
    assert {c['method'] for c in callers}=={'brokerFieldsComeFromElevenReadsAndMutableDiskNumberIsCapturedOnce','queueCountAndBytesAreNotLostAndRemainIndependentOfLaterFixtureChanges'}
    row=dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,helperMethod=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=callers[0],associatedCurrentCases=callers,kind='BORROWED_INTERFACE_DEFINITION_LOADER',disposition='REQUIRED_CONTRACT',reason='The owned JavaSE fixture creates a proxy of the borrowed ClientSession interface using the loader that actually defines that interface. An arbitrary thread-context loader is not guaranteed to see the SDK type. The handler throws AssertionError on every invocation; the two actual tests use injected readers and never use a real Core session. This loader selects type visibility, not a connection, startup authority or production component. Source/current callers and zero query/outer operations are independently bound; raw warning is retained.',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=[row]));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=1,existingLoaderReferencesReauthenticated=1,newSourceReasons=0,rawRetained=1,associatedActualCallers=2,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
