"""Independent inverse of original86 oracle bodies; explicit new closed-candidate oracle and mutation rejection."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11320_batch_source_guard_source_post import span,declaration_end,replace_once

OUT=data.BASE/'PG11378-full-payload-guard-source-post-v1'


def locate(tokens,pattern):
    found=[i for i in range(len(tokens)-len(pattern)+1) if tokens[i:i+len(pattern)]==pattern]
    if len(found)!=1:
        raise ValueError('one exact fixed source sequence')
    return found[0]


def block(tokens,header):
    a=locate(tokens,canonical(header))+len(canonical(header))
    depth=1
    for b in range(a,len(tokens)):
        depth+=(tokens[b]=='{')-(tokens[b]=='}')
        if not depth:
            return a,b
    raise ValueError('complete fixed body')


def new_case(role):
    # Independent literal 2195 failure vector, not calculated using any Production method.
    return canonical('''@Test void ROLEfull013HelperReleasesRejectedCandidateBeforeReturningOwner() {
      var probe = new FullProbe(); try {
        probe.close(); assertEquals(1,probe.closes.get());
        var failure=assertThrows(IllegalStateException.class,()->fullOwner(probe));
        assertEquals("standard metric registry closed",failure.getMessage());
        assertEquals(2,probe.closes.get()); assertEquals(0,probe.scrapes.get()); assertTrue(probe.isClosed());
      } finally { probe.close(); }
    }'''.replace('ROLE',role))


def inverse(before,after,role):
    old=canonical(before)
    tokens=canonical(after) if isinstance(after,str) else list(after)
    replace_once(tokens,new_case(role),[])
    header='private static final class FullProbe extends io.micrometer.prometheusmetrics.PrometheusMeterRegistry {'
    a,b=block(tokens,header)
    body=tokens[a:b]
    replace_once(body,canonical('final AtomicInteger closes=new AtomicInteger();'),[])
    replace_once(body,canonical('@Override public void close(){closes.incrementAndGet();super.close();}'),[])
    tokens[a:b]=body
    header='private static '+role.capitalize()+'StandardMetricSource fullOwner(FullProbe probe) {'
    a,b=block(old,header);original=old[a:b];split=declaration_end(original)
    mode='DEBUG_MODE' if role=='batch' else '"DEBUG"'
    if original[split:]!=canonical('owner.bind('+mode+');return owner;'):
        raise ValueError('original fixed factory helper oracle')
    x,y=block(tokens,header)
    expected=original[:split]+canonical('boolean transferred=false;try{owner.bind('+mode+');transferred=true;return owner;}finally{if(!transferred)owner.close();}')
    if tokens[x:y]!=expected:
        raise ValueError('owner guard before bind and transfer only on completed bind')
    tokens[x:y]=original
    if role!='batch':
        name=role+'full011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership'
        a,b=span(old,name);original=old[a:b]
        declaration=canonical('var executor=Executors.newFixedThreadPool(4);')
        start=locate(original,declaration);rest=original[start+len(declaration):]
        end=locate(rest,canonical('Reference.reachabilityFence(bundle);'))
        expected=original[:start]+canonical('try(var executor=Executors.newFixedThreadPool(4)){')+rest[:end]+['}']+rest[end:]
        x,y=span(tokens,name)
        if tokens[x:y]!=expected:
            raise ValueError('original011 worker/finally/30second oracle with executor TWR')
        tokens[x:y]=original
        name=role+'full012CallerCloseBetweenSourcesCannotReturnPartialText'
        a,b=span(old,name);original=old[a:b]
        owner=canonical('var standard=fullOwner(probe);')
        end=locate(original,owner)+len(owner)
        declaration=canonical('var executor=Executors.newSingleThreadExecutor();')
        if original[end:end+len(declaration)]!=declaration:
            raise ValueError('original012 retained owner then executor declaration')
        expected=original[:end]+canonical('try{try(var executor=Executors.newSingleThreadExecutor()){')+original[end+len(declaration):]+canonical('}}finally{standard.close();}')
        x,y=span(tokens,name)
        if tokens[x:y]!=expected:
            raise ValueError('original012 oracle/finally preserved within immediate owner guard and executor TWR')
        tokens[x:y]=original
    if tokens!=old:
        raise ValueError('all original86 oracle/import/helper/other Test tokens preserved')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11376-full-payload-guard-plan-v1/manifest.json'
    plan=data.read_checked(p,'e47458abf5001c4223103f526be3203deb0328a1e5776c56a101e74849fbe264')
    normal=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json',
        '46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==3 and plan['originalMethods']==86 and plan['addedMethods']==3
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();role=row['role']
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,role)
        base=canonical(after)
        mutations=[(canonical('transferred=true;'),canonical('transferred=false;')),
            (canonical('if(!transferred)owner.close();'),canonical('if(transferred)owner.close();')),
            (canonical('if(!transferred)owner.close();'),canonical('if(!transferred)unrelated.close();')),
            (canonical('assertEquals("standard metric registry closed",failure.getMessage());'),canonical('assertEquals("wrong",failure.getMessage());')),
            (canonical('assertEquals(2,probe.closes.get());'),canonical('assertEquals(3,probe.closes.get());')),
            (new_case(role),[])]
        if role!='batch':
            mutations += [(canonical('try(var executor=Executors.newFixedThreadPool(4)){'),canonical('try(var executor=Executors.newFixedThreadPool(3)){')),
                (canonical('assertTrue(executor.awaitTermination(30,TimeUnit.SECONDS));standard.close();'),canonical('assertTrue(executor.awaitTermination(29,TimeUnit.SECONDS));standard.close();'))]
        for pattern,replacement in mutations:
            bad=list(base);replace_once(bad,pattern,replacement)
            try:
                inverse(before,bad,role)
            except ValueError:
                negatives+=1
            else:
                raise AssertionError('changed ownership/oracle/deadline vector accepted')
    assert negatives==22
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,
        originalMethods=86,addedIndependentMethods=3,helperTransferGuards=3,outerOwnerGuards=2,executorTwr=4,metadataNegativeVectors=negatives,
        productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
