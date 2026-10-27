"""Independent per-method inverse of14 owner guards and executor TWR; all original16 oracle tokens retained."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT=data.BASE/'PG11320-batch-source-guard-source-post-v1'


def span(tokens,name):
    positions=[i for i in range(len(tokens)-1) if tokens[i:i+2]==['void',name]]
    if len(positions)!=1:
        raise ValueError('one exact existing Test method')
    left=tokens.index('{',positions[0])
    depth=1
    for i in range(left+1,len(tokens)):
        depth+=(tokens[i]=='{')-(tokens[i]=='}')
        if depth==0:
            return left+1,i
    raise ValueError('closed original method body')


def declaration_end(body):
    positions=[i for i in range(len(body)-2) if body[i:i+3]==['var','owner','=']]
    if len(positions)!=1:
        raise ValueError('one retained owner declaration')
    nesting=[]
    for i in range(positions[0],len(body)):
        token=body[i]
        if token in ('(','{','['):
            nesting.append(token)
        elif token in (')','}',']'):
            expected={')':'(','}':'{',']':'['}[token]
            if not nesting or nesting.pop()!=expected:
                raise ValueError('balanced owner declaration')
        if token==';' and not nesting:
            return i+1
    raise ValueError('owner declaration terminator')


def replace_once(tokens,before,after):
    positions=[i for i in range(len(tokens)-len(before)+1) if tokens[i:i+len(before)]==before]
    if len(positions)!=1:
        raise ValueError('exact single original executor lifetime boundary')
    i=positions[0]
    tokens[i:i+len(before)]=after


def undo_executor(rest):
    replace_once(rest,canonical('try (var executor = Executors.newFixedThreadPool(2)) { try {'),
        canonical('var executor = Executors.newFixedThreadPool(2); try {'))
    replace_once(rest,canonical('assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS)); owner.close(); } }'),
        canonical('assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS)); owner.close(); }'))


def inverse(before,after,methods):
    old=canonical(before)
    tokens=canonical(after) if isinstance(after,str) else list(after)
    for low,high,name in sorted(((*span(tokens,n),n) for n in methods),reverse=True):
        a,b=span(old,name)
        original=old[a:b]
        body=tokens[low:high]
        split=declaration_end(body)
        original_split=declaration_end(original)
        if body[:split]!=original[:original_split]:
            raise ValueError('original owner declaration, inputs and prelude preserved')
        rest=body[split:]
        tail=canonical('} finally { owner.close(); }')
        if rest[:2]!=['try','{'] or rest[-len(tail):]!=tail:
            raise ValueError('guard begins immediately after owner declaration and closes same owner')
        restored=rest[2:-len(tail)]
        if name.startswith('batchhost016'):
            undo_executor(restored)
        if restored!=original[original_split:]:
            raise ValueError('original expected, assertion, close/retry order, identity or deadline changed')
        tokens[low:high]=original
    if tokens!=old:
        raise ValueError('all other original Test and helper tokens unchanged')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11318-batch-source-guard-plan-v1/manifest.json'
    plan=data.read_checked(p,'9e5ded873f7abbb9ee67331a1ab109899375b627c084739cfdf2270a00cc34b6')
    normal=data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json',
        'e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert plan['actualExit']==0 and plan['ownerGuards']==len(plan['guardedMethods'])==14 and plan['executorTwr']==1
    assert len(plan['sourceChanges'])==1
    row=plan['sourceChanges'][0]
    path=row['path']
    before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
    assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=path)
    methods=plan['guardedMethods']
    inverse(before,after,methods)
    base=canonical(after)
    bads=[]
    for name in methods:
        low,high=span(base,name)
        body=base[low:high]
        split=declaration_end(body)
        tail=canonical('} finally { owner.close(); }')
        bad=list(base)
        bad[low:high]=body[:split]+body[split+2:-len(tail)]
        bads.append(bad)
        bad=list(base)
        tail_start=high-len(tail)
        assert bad[tail_start+3]=='owner'
        bad[tail_start+3]='unrelatedOwner'
        bads.append(bad)
    bads.append(canonical(after.replace('@Test','@Disabled',1)))
    name=next(n for n in methods if n.startswith('batchhost016'))
    low,high=span(base,name)
    body=list(base[low:high])
    split=declaration_end(body)
    tail=canonical('} finally { owner.close(); }')
    rest=body[split+2:-len(tail)]
    undo_executor(rest)
    bad=list(base)
    bad[low:high]=body[:split+2]+rest+tail
    bads.append(bad)
    bad=list(base)
    replace_once(bad,canonical('assertTrue(entered.await(10,TimeUnit.SECONDS));'),canonical('assertTrue(entered.await(9,TimeUnit.SECONDS));'))
    bads.append(bad)
    for bad in bads:
        try:
            inverse(before,bad,methods)
        except ValueError:
            pass
        else:
            raise AssertionError('missing guard/owner/TWR/deadline or altered original oracle accepted')
    assert len(bads)==31
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],
        planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],guardedMethods=methods,ownerGuards=14,executorTwr=1,
        metadataNegativeVectors=len(bads),allOriginalOracleTokensRestored=True,originalCloseRetryAndDeadlineTokensRestored=True,
        allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
