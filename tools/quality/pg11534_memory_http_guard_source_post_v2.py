"""Independent original44 inverse and104 guard/oracle metadata negatives; two fixed cleanup vectors."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11320_batch_source_guard_source_post import replace_once
from pg11378_full_payload_guard_source_post import locate
from pg11442_gc_fake_guard_source_post import end_brace

OUT=data.BASE/'PG11534-memory-http-guard-source-post-v2'

def case_body(role):
    return canonical('@Test void '+role+'''mhttp023CallerFailureStillCleansOnceAndCompletedCloseIsNotRepeated(){
      var exchange=new Exchange(GET_METHOD,PATH);
      try{
        var failure=new AssertionError("caller cleanup fixture");assertFalse(exchange.closed);
        assertSame(failure,assertThrows(AssertionError.class,()->{
          try{throw failure;}finally{if(!exchange.closed)exchange.close();}
        }));
        assertTrue(exchange.closed);assertEquals(1,exchange.closeCalls);
        if(!exchange.closed)exchange.close();assertEquals(1,exchange.closeCalls);
      }finally{if(!exchange.closed)exchange.close();}
    }''')

def guard_spans(tokens):
    rows=[]
    for i in range(1,len(tokens)-1):
        if tokens[i:i+2]!=['try','{'] or tokens[i-1]!=';':
            continue
        j=i-2
        while j>=0 and tokens[j] not in (';','{','}'):
            j-=1
        declaration=tokens[j+1:i]
        if len(declaration)<8 or declaration[0]!='var' or declaration[2:6]!=['=','new','Exchange','('] or declaration[-2:]!=[')', ';']:
            continue
        variable=declaration[1]
        if variable not in ('exchange','first','second','missing'):
            raise ValueError('known exact fixture variable')
        closing=end_brace(tokens,i+1)
        tail=canonical('finally{if(!'+variable+'.closed)'+variable+'.close();}')
        if tokens[closing+1:closing+1+len(tail)]==tail:
            rows.append((i,closing+1+len(tail),closing,variable))
    return rows

def inverse(before,after,role):
    tokens=canonical(after) if isinstance(after,str) else list(after)
    replace_once(tokens,case_body(role),[])
    count=0
    while True:
        spans=guard_spans(tokens)
        if not spans:
            break
        start,end,closing,_=spans[0];tokens[start:end]=tokens[start+2:closing];count+=1
    if count!=25 or tokens!=canonical(before):
        raise ValueError('exact25 same-candidate immediate guards; every original22 oracle/body/close/byte token restored')

def mutations(after,role):
    tokens=canonical(after);limit=locate(tokens,case_body(role));spans=guard_spans(tokens[:limit]);assert len(spans)==25
    bads=[]
    for start,end,closing,variable in spans:
        bad=list(tokens);bad[start:end]=bad[start+2:closing];bads.append(bad)
        bad=list(tokens);tail=canonical('finally{if(!'+variable+'.closed)'+variable+'.close();}')
        assert bad[closing+1:end]==tail
        bad[closing+1:end]=canonical('finally{if(!'+variable+'.closed)unrelated.close();}');bads.append(bad)
    bad=list(tokens);replace_once(bad,canonical('@Test void '+role+'mhttp001()'),canonical('@Disabled void '+role+'mhttp001()'));bads.append(bad)
    bad=list(tokens);case=case_body(role);a=locate(bad,case);part=list(case);p=locate(part,canonical('assertEquals(1,exchange.closeCalls);if(!exchange.closed)exchange.close();'))
    part[p:p+len(canonical('assertEquals(1,exchange.closeCalls);'))]=canonical('assertEquals(2,exchange.closeCalls);')
    bad[a:a+len(case)]=part;bads.append(bad)
    assert len(bads)==52
    return bads

def main():
    invocation=capture(__file__);assert not OUT.exists()
    p=data.BASE/'PG11532-memory-http-guard-plan-v1/manifest.json';plan=data.read_checked(p,'98903e7ff842af1c41a400a12fbcbf0ab595e01b1579b6c30034efad1296640b')
    normal=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    paths={r['path'] for r in plan['sourceChanges']};assert len(paths)==2 and plan['candidateGuards']==50
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in paths)
    count=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();role=row['role']
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,role)
        for bad in mutations(after,role):
            try:
                inverse(before,bad,role)
            except ValueError:
                count+=1
            else:
                raise AssertionError('changed guard/candidate/original oracle/new fixed count accepted')
    assert count==104
    rejected=data.ROOT/"tools/quality/pg11534_memory_http_guard_source_post.py"
    assert data.sha(rejected.read_bytes())=="2a2c8ad5c8eafad85a877b133be254081e89f4bea1ed60c4ef3359c6f1f1af91"
    assert not (data.BASE/"PG11534-memory-http-guard-source-post-v1").exists()
    verify(invocation);OUT.mkdir()
    data.write(OUT/"rejected-source-post-v1.json",dict(actualExit=1,toolSha256=data.sha(rejected.read_bytes()),outNotCreated=True,reason="REPEATED_FIXED_ASSERT_NOT_UNIQUE_ANCHOR",productTestsExecuted=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],candidateGuards=50,originalMethods=44,addedIndependentMethods=2,metadataNegativeVectors=count,
        allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
