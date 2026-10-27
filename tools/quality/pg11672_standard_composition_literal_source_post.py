"""Independent full26 oracle inverse and28 wrong literal/reference/disabled metadata vectors."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11208_web_supplied_metric_fixture_source_post import inverse

OUT=data.BASE/'PG11672-standard-composition-literal-source-post-v1'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11670-standard-composition-literal-plan-v1/manifest.json'
    plan=data.read_checked(p,'af6206742ae9e6e6f362b5a0d4695d137890ed373b2f9c4167781c974b982b3a')
    normal=data.read_checked(data.BASE/'PG11644-db-pool-binding-fatal-case-six-compile-v1/manifest.json',
        'b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==2 and plan['stringConstants']==12 and plan['referencesReplaced']==76
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
    assert count==28
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],stringConstants=12,referencesReplaced=76,
        allOriginalOracleTokensRestored=True,allOriginalGuardAndDeadlineTokensRestored=True,allMainAndOtherInputsPreserved=True,
        originalMethods=26,metadataNegativeVectors=count,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
