"""Independent inverse of32String and one factory int with thirteen metadata negatives."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded
from pg11104_web_pure_value_source_post import remove

OUT=data.BASE/'PG11208-web-supplied-metric-fixture-source-post-v1'


def inverse(before,after,rows):
    tokens=canonical(after)
    if 'FAILURE_FACTORY_CALL' in tokens:
        remove(tokens,canonical('private static final int FAILURE_FACTORY_CALL = 2;'))
        if tokens.count('FAILURE_FACTORY_CALL')!=1:
            raise ValueError('single original second-factory boundary')
        tokens=['2' if t=='FAILURE_FACTORY_CALL' else t for t in tokens]
    for row in rows:
        remove(tokens,canonical('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name'])!=row['references']:
            raise ValueError('every original fixed literal preserved')
        literal=canonical(row['literal'])
        assert len(literal)==1
        tokens=[literal[0] if t==row['name'] else t for t in tokens]
    if folded(tokens)!=canonical(before):
        raise ValueError('original independent golden, assertion, boundary or callee changed')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11206-web-supplied-metric-fixture-plan-v1/manifest.json'
    plan=data.read_checked(p,PLAN_SHA)
    normal=data.read_checked(data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json','b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==4 and plan['actualExit']==0 and plan['stringConstants']==32 and plan['factoryCallConstants']==1
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0
    for row in plan['sourceChanges']:
        path=row['path']
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,row['constants'])
        first=row['constants'][0]
        declaration='private static final String '+first['name']+' = '+first['literal']+';'
        bads=[after.replace(first['literal'],'"wrong-fixed-vector"',1),after.replace(declaration,'',1),after.replace('@Test','@Disabled',1)]
        if row['factoryCallConstant'] is not None:
            bads.append(after.replace('FAILURE_FACTORY_CALL = 2','FAILURE_FACTORY_CALL = 3',1))
        for bad in bads:
            assert bad!=after
            try:
                inverse(before,bad,row['constants'])
            except ValueError:
                negatives+=1
            else:
                raise AssertionError('changed original fixture accepted')
    assert negatives==13
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],stringConstants=32,factoryCallConstants=1,referencesReplaced=plan['referencesReplaced'],
        metadataNegativeVectors=negatives,allMainAndOtherInputsPreserved=True,allOriginalOracleTokensRestored=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


PLAN_SHA='7343097d7d599f6d094f0ea225b7ee5a6aac2869f1e61a60e81cdd8783461e6b'

if __name__=='__main__':
    main()
