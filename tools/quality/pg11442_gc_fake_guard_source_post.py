"""Independent42 original-oracle inverse, six fixed cleanup vectors and63 guard/confirmation mutations."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11320_batch_source_guard_source_post import replace_once
from pg11378_full_payload_guard_source_post import block,locate

OUT=data.BASE/'PG11442-gc-fake-guard-source-post-v1'


def case_body(role,number):
    if number==15:
        name=role+'gc015ConfirmedFixtureCloseIsNotRepeatedByCleanupGuard'
        body='''var resource=new Fake();try {
          assertFalse(resource.closeConfirmed);resource.close();assertTrue(resource.closeConfirmed);
          if(!resource.closeConfirmed)resource.close();assertEquals(1,resource.closeInvocations.get());
        }finally{if(!resource.closeConfirmed)resource.close();}'''
    else:
        name=role+'gc016FailedFixtureCloseRemainsUnconfirmedUntilExplicitRetry'
        body='''for(boolean priorSuccess:List.of(false,true)){
          for(Throwable failure:List.of(new IllegalStateException("cleanup runtime fixture"),new AssertionError("cleanup fatal fixture"))){
            var resource=new Fake();try{
              if(priorSuccess)resource.close();resource.onCloseCallback=()->fail(failure);
              assertSame(failure,assertThrows(failure.getClass(),resource::close));assertFalse(resource.closeConfirmed);
              assertEquals(priorSuccess?2:1,resource.closeInvocations.get());resource.onCloseCallback=()->{};
              if(!resource.closeConfirmed)resource.close();assertTrue(resource.closeConfirmed);
              assertEquals(priorSuccess?3:2,resource.closeInvocations.get());
            }finally{resource.onCloseCallback=()->{};if(!resource.closeConfirmed)resource.close();}
          }
        }'''
    return canonical('@Test void '+name+'(){'+body+'}')


def end_brace(tokens,start):
    depth=1
    for i in range(start+1,len(tokens)):
        depth+=(tokens[i]=='{')-(tokens[i]=='}')
        if not depth:
            return i
    raise ValueError('complete guard block')


def guard_spans(tokens,limit):
    result=[]
    for i in range(limit-1):
        if tokens[i:i+2]!=['try','{']:
            continue
        end=end_brace(tokens,i+1)
        for variable in ('resource','one','two'):
            declaration=canonical('var '+variable+'=new Fake();')
            tail=canonical('finally{if(!'+variable+'.closeConfirmed)'+variable+'.close();}')
            if i>=len(declaration) and tokens[i-len(declaration):i]==declaration and tokens[end+1:end+1+len(tail)]==tail:
                result.append((i,end+1+len(tail),end,variable))
    return result


def inverse(before,after,role):
    original=canonical(before)
    tokens=canonical(after) if isinstance(after,str) else list(after)
    for n in (15,16):
        replace_once(tokens,case_body(role,n),[])
    a,b=block(tokens,'private static final class Fake extends JvmGcMetrics {')
    fake=tokens[a:b]
    replace_once(fake,canonical('boolean closeConfirmed;'),[])
    x,y=block(fake,'public void close(){')
    if fake[x:y]!=canonical('closeConfirmed=false;closeInvocations.incrementAndGet();onCloseCallback.run();closeConfirmed=true;'):
        raise ValueError('logical close confirmed only after callback normal completion, cleared before any retry')
    fake[x:y]=canonical('closeInvocations.incrementAndGet();onCloseCallback.run();')
    tokens[a:b]=fake
    count=0
    while True:
        spans=guard_spans(tokens,len(tokens))
        if not spans:
            break
        i,end,closing,_=spans[0]
        tokens[i:end]=tokens[i+2:closing]
        count+=1
    if count!=8 or tokens!=original:
        raise ValueError('eight immediate same-candidate guards only; every original14 oracle/identity/order/deadline token restored')


def mutations(after,role):
    tokens=canonical(after)
    limit=locate(tokens,canonical('@Test void '+role+'gc015ConfirmedFixtureCloseIsNotRepeatedByCleanupGuard(){'))
    spans=guard_spans(tokens,limit)
    assert len(spans)==8
    bads=[]
    for i,end,closing,variable in spans:
        bad=list(tokens);bad[i:end]=bad[i+2:closing];bads.append(bad)
        bad=list(tokens)
        expected=canonical('finally{if(!'+variable+'.closeConfirmed)'+variable+'.close();}')
        altered=canonical('finally{if(!'+variable+'.closeConfirmed)unrelated.close();}')
        assert bad[closing+1:end]==expected
        bad[closing+1:end]=altered;bads.append(bad)
    for pattern,replacement in [
        ('onCloseCallback.run();closeConfirmed=true;','closeConfirmed=true;onCloseCallback.run();'),
        ('closeConfirmed=false;',''),
        ('@Test','@Disabled'),
        ('assertEquals(priorSuccess?3:2,resource.closeInvocations.get());','assertEquals(priorSuccess?3:3,resource.closeInvocations.get());')]:
        bad=list(tokens)
        if pattern=='@Test':
            a=locate(tokens[:locate(tokens,canonical('@Test void '+role+'gc002StandardIsLazyForSourceFactoryAndOwner(){'))],canonical('@Test'))
            bad[a:a+2]=canonical(replacement)
        else:
            replace_once(bad,canonical(pattern),canonical(replacement))
        bads.append(bad)
    bad=list(tokens)
    case=case_body(role,15)
    a=locate(bad,case);part=list(case)
    replace_once(part,canonical('assertEquals(1,resource.closeInvocations.get());'),canonical('assertEquals(2,resource.closeInvocations.get());'))
    bad[a:a+len(case)]=part;bads.append(bad)
    assert len(bads)==21
    return bads


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11440-gc-fake-guard-plan-v1/manifest.json'
    plan=data.read_checked(p,'b6db4212c303e9a54ae3cc7b21b739de7cddaadb2d0f8affbd591082c94e781e')
    normal=data.read_checked(data.BASE/'PG11412-api-web-payload-literal-six-compile-v1/manifest.json',
        'b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    paths={r['path'] for r in plan['sourceChanges']}
    assert len(paths)==3 and plan['candidateGuards']==24
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in paths)
    count=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();role=row['role']
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,role)
        for bad in mutations(after,role):
            try:
                inverse(before,bad,role)
            except ValueError:
                count+=1
            else:
                raise AssertionError('changed candidate guard/close confirmation/independent oracle accepted')
    assert count==63
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],candidateGuards=24,
        originalMethods=42,addedIndependentMethods=6,metadataNegativeVectors=count,allOriginalOracleTokensRestored=True,
        allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
