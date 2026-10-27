"""Independent current XML/span/case/owner checks with eight metadata negatives, no product replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='eee3d32be87396f61f94e6013f4864330ceee4f3'
OUT=data.BASE/'PG11713-jvm-system-owner-context-post-v1'
PIN='87b6809f45d7227b9ed1bb8e8deb642a3885b88c57492b319d550c3d5f96efe9'

def main():
    invocation=capture(__file__);assert not OUT.exists();cp=data.BASE/'PG11711-jvm-system-owner-context-v1';m=data.read_checked(cp/'manifest.json',PIN);review=data.read_checked(cp/'review.json',m['reviewSha256'])
    host=data.read_checked(data.BASE/'PG11706-jvm-system-literal-host-v1/manifest.json','4d0ea9f465242330d41e634af31aa1fc5222e2f6f6a22a16286cce49cafe1d57')
    sp=data.BASE/'PG11708-jvm-system-literal-static-v1';st=data.read_checked(sp/'manifest.json','1c4dfa2d0c8d054f3588ab1c4391912ac6d339c00dc2337db64670b05e8155ae');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual={(str(Path(f.get('name')).relative_to(data.ROOT)),tuple(sorted(n.attrib.items()))) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);thread=a['rule']=='DoNotUseThreads'
        expected_case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        expected=dict(source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=expected_case,disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason') or (path,tuple(sorted(a.items()))) not in actual:raise ValueError('exact current source/case/span/owner contract required')
        assert data.sha(text.encode())==expected['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        if thread:
            assert name.endswith('014FiniteConcurrentPortsDoNotShareSourceState') and 'try(varworkers=Executors.newFixedThreadPool(4)){' in compact and 'i<64' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact and ('assertEquals(256,total.get());' if 'JvmMetricsTest' in path else 'assertEquals(128,total.get());') in compact
        else:
            assert name.endswith(('006ClosedDebugFailsBeforeFactoryAndDoesNotReopen','012StandardOnClosedOwnerDoesNotInspectOrCloseAgain')) and compact.count('source.close();')==1 and 'varsource=newRegistry();source.close();' in compact and ('assertEquals(before,source.closes.get());' in compact or 'assertEquals(closes,source.closes.get());' in compact)
        assert any(c['classname']==expected_case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(actual)==len({r['id'] for r in rows})==16 and sum(r['newSourceReason'] for r in rows)==8
    for row in rows:validate(row)
    first=rows[0];negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(first);bad[field]=value;assert bad!=first
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid source contract metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=16,existingThreadReferencesReauthenticated=8,newClosedRegistryReasons=8,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
