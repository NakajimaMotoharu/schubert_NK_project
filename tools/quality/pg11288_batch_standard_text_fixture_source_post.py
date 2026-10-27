"""Independent inverse of25Strings and two first-binder boundaries with twenty metadata negatives."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded
from pg11104_web_pure_value_source_post import remove

OUT=data.BASE/'PG11288-batch-standard-text-fixture-source-post-v1'


def inverse(before,after,rows):
    tokens=canonical(after)
    if 'FIRST_BINDER_POSITION' in tokens:
        remove(tokens,canonical('private static final int FIRST_BINDER_POSITION = 1;'))
        if tokens.count('FIRST_BINDER_POSITION')!=1:
            raise ValueError('single original first-binder boundary')
        tokens=['1' if t=='FIRST_BINDER_POSITION' else t for t in tokens]
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
    p=data.BASE/'PG11286-batch-standard-text-fixture-plan-v1/manifest.json'
    plan=data.read_checked(p,PLAN_SHA)
    normal=data.read_checked(data.BASE/'PG11264-http-recorder-fixture-six-compile-v1/manifest.json','87b29c22a2f3b612936173d8633cd67201368bc1f711938a0f1e834624f17d9f')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==6 and plan['actualExit']==0 and plan['stringConstants']==25 and plan['firstBinderConstants']==2
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
        if row['firstBinderConstant'] is not None:
            bads.append(after.replace('FIRST_BINDER_POSITION = 1','FIRST_BINDER_POSITION = 2',1))
        for bad in bads:
            assert bad!=after
            try:
                inverse(before,bad,row['constants'])
            except ValueError:
                negatives+=1
            else:
                raise AssertionError('changed original fixture accepted')
    assert negatives==20
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],stringConstants=25,firstBinderConstants=2,referencesReplaced=plan['referencesReplaced'],
        metadataNegativeVectors=negatives,allMainAndOtherInputsPreserved=True,allOriginalOracleTokensRestored=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


PLAN_SHA='70f577eb77407b8d0dc466325cd035b1d23bcd554dd9d8aa810f1c90c30070fc'

if __name__=='__main__':
    main()
