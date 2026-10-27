"""Independently restore both role originals from four same literals and28 guards/two TWR;68 negatives."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from pg11320_batch_source_guard_source_post import span,declaration_end,replace_once,undo_executor

OUT=data.BASE/'PG11346-api-web-source-guard-source-post-v1'


def inverse(before,after,methods,constants):
    old=canonical(before)
    tokens=canonical(after) if isinstance(after,str) else list(after)
    for row in constants:
        remove(tokens,canonical('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name'])!=row['references']:
            raise ValueError('all original independent fixed mode literal sites')
        literal=canonical(row['literal'])
        assert len(literal)==1
        tokens=[literal[0] if t==row['name'] else t for t in tokens]
    for low,high,name in sorted(((*span(tokens,n),n) for n in methods),reverse=True):
        a,b=span(old,name)
        original=old[a:b]
        body=tokens[low:high]
        split=declaration_end(body)
        original_split=declaration_end(original)
        if body[:split]!=original[:original_split]:
            raise ValueError('original role owner declaration and inputs')
        rest=body[split:]
        tail=canonical('} finally { owner.close(); }')
        if rest[:2]!=['try','{'] or rest[-len(tail):]!=tail:
            raise ValueError('immediate owner guard and exact same cleanup owner')
        restored=rest[2:-len(tail)]
        if 'host016' in name:
            undo_executor(restored)
        if restored!=original[original_split:]:
            raise ValueError('original role diagnostic, oracle, close/retry, identity or deadline changed')
        tokens[low:high]=original
    if tokens!=old:
        raise ValueError('original package/import/otherTest/helper tokens unchanged')


def negatives(after,methods,constants):
    base=canonical(after)
    bads=[]
    tail=canonical('} finally { owner.close(); }')
    for name in methods:
        low,high=span(base,name)
        body=base[low:high]
        split=declaration_end(body)
        bad=list(base)
        bad[low:high]=body[:split]+body[split+2:-len(tail)]
        bads.append(bad)
        bad=list(base)
        owner_position=high-len(tail)+3
        assert bad[owner_position]=='owner'
        bad[owner_position]='unrelatedOwner'
        bads.append(bad)
    bads.append(canonical(after.replace('@Test','@Disabled',1)))
    name=next(n for n in methods if 'host016' in n)
    low,high=span(base,name)
    body=base[low:high]
    split=declaration_end(body)
    rest=body[split+2:-len(tail)]
    undo_executor(rest)
    bad=list(base)
    bad[low:high]=body[:split+2]+rest+tail
    bads.append(bad)
    bad=list(base)
    replace_once(bad,canonical('assertTrue(entered.await(10,TimeUnit.SECONDS));'),canonical('assertTrue(entered.await(9,TimeUnit.SECONDS));'))
    bads.append(bad)
    first=constants[0]
    declaration='private static final String '+first['name']+' = '+first['literal']+';'
    assert declaration in after
    bads.append(canonical(after.replace(first['literal'],'"wrong-fixed-mode"',1)))
    bads.append(canonical(after.replace(declaration,'',1)))
    bad=list(base)
    index=max(i for i,t in enumerate(bad) if t==first['name'])
    bad[index]='"changed-mode-site"'
    bads.append(bad)
    assert len(bads)==34
    return bads


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11344-api-web-source-guard-plan-v1/manifest.json'
    plan=data.read_checked(p,'82dadcf32291197184759d2a2583ccf54ad2bd78d95a2174c1d5b78341006680')
    normal=data.read_checked(data.BASE/'PG11322-batch-source-guard-six-compile-v1/manifest.json',
        '066e1c301187c43224e8ab120c50889ef8a832f48de3fe4406aa7e533ac14e27')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==2 and plan['actualExit']==0 and plan['ownerGuards']==28 and plan['executorTwr']==2 and plan['stringConstants']==4
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    count=0
    for row in plan['sourceChanges']:
        path=row['path']
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,row['guardedMethods'],row['constants'])
        for bad in negatives(after,row['guardedMethods'],row['constants']):
            try:
                inverse(before,bad,row['guardedMethods'],row['constants'])
            except ValueError:
                count+=1
            else:
                raise AssertionError('invalid role literal/guard/owner/TWR/deadline or changed original expected accepted')
    assert count==68
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],planManifestSha256=data.sha(p.read_bytes()),
        sourceChanges=plan['sourceChanges'],ownerGuards=28,executorTwr=2,stringConstants=4,referencesReplaced=plan['referencesReplaced'],
        originalMethods=32,originalSuites=2,metadataNegativeVectors=count,allOriginalOracleTokensRestored=True,
        originalRoleDiagnosticsImportsCloseRetryAndDeadlineTokensRestored=True,allMainAndOtherInputsPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
