"""Independent token inverse of owned TWR scopes, normal close assertions and same-value boundary."""
from collections import defaultdict
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT=data.BASE/'PG11078-inbox-value-lifecycle-source-post-v1'


def replace(tokens,pattern,result,count):
    positions=[i for i in range(len(tokens)-len(pattern)+1) if tokens[i:i+len(pattern)]==pattern]
    if len(positions)!=count:
        raise ValueError('exact introduced token sites required')
    for i in reversed(positions):
        tokens[i:i+len(pattern)]=result


def closing(tokens,start):
    depth=1
    for end in range(start+1,len(tokens)):
        depth+=(tokens[end]=='{')-(tokens[end]=='}')
        if depth==0:
            return end
    raise ValueError('complete finite method/try body required')


def inverse(stem,before,after,wrappers):
    tokens=canonical(after)
    if stem=='SecretBufferTest':
        replace(tokens,canonical('import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;'),[],1)
        replace(tokens,canonical('private static final int MAXIMUM_FIXTURE_CAPACITY = 1_050_000;'),[],1)
        replace(tokens,['MAXIMUM_FIXTURE_CAPACITY'],canonical('1_050_000'),1)
        for name,count in [('stream',2),('request',1)]:
            replace(tokens,canonical('assertDoesNotThrow('+name+'::close)'),canonical(name+'.close()'),count)
    methods=defaultdict(list)
    for wrapper in wrappers:
        methods[wrapper['method']].append(wrapper)
    for method,items in methods.items():
        positions=[i for i,t in enumerate(tokens) if t==method and i and tokens[i-1]=='void']
        if len(positions)!=1:
            raise ValueError('original one named Test method required')
        start=next(i for i in range(positions[0],len(tokens)) if tokens[i]=='{')
        end=closing(tokens,start)
        body=tokens[start+1:end]
        for wrapper in reversed(items):
            declarations=canonical(wrapper['declarations'])
            if declarations[-1]!=';':
                raise ValueError('original complete declarations required')
            pattern=['try','(']+declarations[:-1]+[')','{']
            hits=[i for i in range(len(body)-len(pattern)+1) if body[i:i+len(pattern)]==pattern]
            if len(hits)!=1:
                raise ValueError('one exact introduced TWR scope required')
            i=hits[0]
            open_brace=i+len(pattern)-1
            finish=closing(body,open_brace)
            body=body[:i]+declarations+body[open_brace+1:finish]+body[finish+1:]
        tokens=tokens[:start+1]+body+tokens[end:]
    if folded(tokens)!=canonical(before):
        raise ValueError('original assertion/vector/fixture/method tokens changed')


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG11076-inbox-value-lifecycle-plan-v1/manifest.json','04d4e128dcdbb500d27404de32b818fb4d84128e7e521ac62425c4f4e2cb9853')
    normal=data.read_checked(data.BASE/'PG11068-inbox-value-six-compile-v1/manifest.json','c0adec1cf3206e0190692c709761803a00f776d3f75c10475294c06e676ea42b')
    snapshot=Path(normal['jars']['api']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==3 and plan['twrOwnedDeclarations']==15 and plan['twrScopes']==8
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0
    for row in plan['sourceChanges']:
        path=row['path']
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(Path(path).stem,before,after,row['wrappers'])
        bads=[after.replace('@Test','@Disabled',1),after.replace('try (','try_broken (',1),after.replace('LAYOUT_VERSION = "001"','LAYOUT_VERSION = "002"',1)]
        if Path(path).stem=='SecretBufferTest':
            bads += [after.replace('MAXIMUM_FIXTURE_CAPACITY = 1_050_000','MAXIMUM_FIXTURE_CAPACITY = 1_050_001',1),
                after.replace('assertDoesNotThrow(stream::close);','',1),after.replace('assertDoesNotThrow(request::close);','',1)]
        for bad in bads:
            assert bad!=after
            try:
                inverse(Path(path).stem,before,bad,row['wrappers'])
            except ValueError:
                negatives+=1
            else:
                raise AssertionError('deleted cleanup/changed boundary/oracle accepted')
    assert negatives==12
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=plan['sourceChanges'],planManifestSha256='04d4e128dcdbb500d27404de32b818fb4d84128e7e521ac62425c4f4e2cb9853',
        twrOwnedDeclarations=15,twrScopes=8,normalCloseAssertionsAdded=3,numericBoundaryReferences=1,metadataNegativeVectors=negatives,
        allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
