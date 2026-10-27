"""Independent full32 oracle inverse and20 wrong literal/reference/disabled metadata vectors."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11208_web_supplied_metric_fixture_source_post import inverse

OUT=data.BASE/'PG11472-api-web-gc-literal-source-post-v1'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11470-api-web-gc-literal-plan-v2/manifest.json'
    plan=data.read_checked(p,'85fd365b478659ece515a86a799f855b0327620b168ac8a7d7d087c1e55e1979')
    normal=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json',
        '0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==2 and plan['stringConstants']==8 and plan['referencesReplaced']==58
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    count=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,row['constants'])
        bads=[after.replace('@Test','@Disabled',1)]
        for constant in row['constants']:
            declaration='private static final String '+constant['name']+' = '+constant['literal']+';'
            assert declaration in after
            bads.extend([after.replace(constant['literal'],'"wrong-independent-vector"',1),after.replace(declaration,'',1)])
        name=row['constants'][0]['name']
        occurrence=[m for m in LEX.finditer(after) if m.group()==name][-1]
        bads.append(after[:occurrence.start()]+'"changed-reference"'+after[occurrence.end():])
        for bad in bads:
            assert bad!=after
            try:
                inverse(before,bad,row['constants'])
            except ValueError:
                count+=1
            else:
                raise AssertionError('changed fixed fixture/original guard/oracle accepted')
    assert count==20
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],stringConstants=8,referencesReplaced=58,
        allOriginalOracleTokensRestored=True,allOriginalGuardAndDeadlineTokensRestored=True,allMainAndOtherInputsPreserved=True,
        originalMethods=32,metadataNegativeVectors=count,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
