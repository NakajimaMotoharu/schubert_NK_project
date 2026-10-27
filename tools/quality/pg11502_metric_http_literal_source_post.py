"""Independent full44 oracle inverse and36 wrong literal/reference/disabled metadata vectors."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11208_web_supplied_metric_fixture_source_post import inverse

OUT=data.BASE/'PG11502-metric-http-literal-source-post-v1'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    p=data.BASE/'PG11500-metric-http-literal-plan-v1/manifest.json'
    plan=data.read_checked(p,'251d3ce57dfad68efc1a8dd970fc144da6d6c0d04056f096a3c0655c3364797b')
    normal=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json',
        '53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']}
    assert len(changed)==2 and plan['stringConstants']==16 and plan['referencesReplaced']==168
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
    assert count==36
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],stringConstants=16,referencesReplaced=168,
        allOriginalOracleTokensRestored=True,allOriginalGuardAndDeadlineTokensRestored=True,allMainAndOtherInputsPreserved=True,
        originalMethods=44,metadataNegativeVectors=count,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
