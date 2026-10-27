"""Independent current XML/span/case/owner checks with eight metadata negatives, no product replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='5a16139a752e2404cd6c26504760f4568ac413fd'
OUT=data.BASE/'PG11683-standard-composition-owner-context-post-v1'
PIN='f95d9c351fa88d09670621a26d29bd918851b1e05c733a30db40ffffbd38d225'

def main():
    invocation=capture(__file__);assert not OUT.exists();cp=data.BASE/'PG11681-standard-composition-owner-context-v1';m=data.read_checked(cp/'manifest.json',PIN);review=data.read_checked(cp/'review.json',m['reviewSha256'])
    host=data.read_checked(data.BASE/'PG11676-standard-composition-literal-host-v1/manifest.json','0b1d596e787572a815067ee1abaf91b5ef18f7b0c89a26c0a6fd58dfa46b570b')
    sp=data.BASE/'PG11678-standard-composition-literal-static-v1';st=data.read_checked(sp/'manifest.json','d8819401772f3a93f4ed5eceb2b2a7ceb7373583b393b74690f2ca1b6f5ae73e');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
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
            assert name.endswith('013FiniteIndependentConcurrentCompositions') and 'try(varworkers=Executors.newFixedThreadPool(4)){' in compact and 'i<64' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact and 'assertEquals(192,total.get());' in compact
        else:
            assert name.endswith(('006ClosedDebugFailsBeforeAnyPhase','011ClosedStandardDoesNotReadOrReclose')) and compact.count('source.close();')==1 and 'varsource=newRegistry();source.close();' in compact and 'assertEquals(1,source.closes.get());' in compact
        assert any(c['classname']==expected_case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(actual)==len({r['id'] for r in rows})==8 and sum(r['newSourceReason'] for r in rows)==4
    for row in rows:validate(row)
    first=rows[0];negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(first);bad[field]=value;assert bad!=first
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid source contract metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=8,existingThreadReferencesReauthenticated=4,newClosedRegistryReasons=4,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
