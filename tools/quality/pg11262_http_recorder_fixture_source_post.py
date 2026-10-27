"""Independently undo eight literals, private rename and TWR while retaining original owner oracles."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded
from pg11104_web_pure_value_source_post import remove

OUT=data.BASE/'PG11262-http-recorder-fixture-source-post-v1'


def replace(tokens,before,after):
    positions=[i for i in range(len(tokens)-len(before)+1) if tokens[i:i+len(before)]==before]
    if len(positions)!=1:
        raise ValueError('one exact owner boundary and original finally required')
    i=positions[0]
    tokens[i:i+len(before)]=after


def inverse(before,after,rows):
    tokens=canonical(after)
    replace(tokens,canonical('try (var executor = Executors.newFixedThreadPool(4)) { try {'),
        canonical('var executor = Executors.newFixedThreadPool(4); try {'))
    replace(tokens,canonical('assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS)); } } assertEquals(64.0,'),
        canonical('assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS)); } assertEquals(64.0,'))
    if 'DURATION_METRIC' not in tokens or 'DURATION' in tokens:
        raise ValueError('private field rename only')
    tokens=['DURATION' if t=='DURATION_METRIC' else t for t in tokens]
    for row in rows:
        remove(tokens,canonical('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name'])!=row['references']:
            raise ValueError('every original independent literal retained')
        literal=canonical(row['literal'])
        assert len(literal)==1
        tokens=[literal[0] if t==row['name'] else t for t in tokens]
    if folded(tokens)!=canonical(before):
        raise ValueError('original assertion, expected, timeout, callee or ownership changed')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11260-http-recorder-fixture-plan-v1/manifest.json'
    plan=data.read_checked(p,'ab8d59ebfbb8c0f5cca8ce3a7cd32f336a470a561c8dddc0b3138eca33920c07')
    normal=data.read_checked(data.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1/manifest.json',
        '5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert len(plan['sourceChanges'])==1 and plan['actualExit']==0 and plan['stringConstants']==8 and plan['ownedExecutorTwr']==1
    row=plan['sourceChanges'][0]
    path=row['path']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=path)
    before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
    assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
    inverse(before,after,row['constants'])
    first=row['constants'][0]
    declaration='private static final String '+first['name']+' = '+first['literal']+';'
    bads=[after.replace(first['literal'],'"wrong-fixed-vector"',1),after.replace(declaration,'',1),after.replace('@Test','@Disabled',1),
        after.replace('executor.awaitTermination(10,','executor.awaitTermination(9,',1),
        after.replace('executor.shutdownNow();','',1),after.replace('try (var executor =','try (var other =',1)]
    for bad in bads:
        assert bad!=after
        try:
            inverse(before,bad,row['constants'])
        except ValueError:
            pass
        else:
            raise AssertionError('invalid fixture or owner postcondition accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],stringConstants=8,referencesReplaced=plan['referencesReplaced'],
        privateFieldRename=plan['privateFieldRename'],ownedExecutorTwr=1,metadataNegativeVectors=len(bads),
        allMainAndOtherInputsPreserved=True,allOriginalOracleTokensRestored=True,originalOwnerFinallyAndTimeoutsRestored=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
