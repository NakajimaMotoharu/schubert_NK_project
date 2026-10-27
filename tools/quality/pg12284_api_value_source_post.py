"""Independent strict raw inverse for all18 original methods; no literal folding or oracle edits."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg12222_check_health_source_post import inverse,raw

OUT=data.BASE/'PG12284-api-value-source-post-v1'
PLAN='350e7513bbd53a67ff76ec960a6e4a17e9360c129a1d5c2149f56a968ff43823'
COUNTS=dict(StubAnswerProviderTest=5,PasswordPolicyTest=3,OutboxDlqMetadataTest=2,GeneratedMetricValueContractTest=8)

def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12285-api-value-plan-v3/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==4 and plan['stringConstants']==9 and plan['stringReferences']==50
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0;catalog=[];tokens=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(after.encode())==row['sha256'] and data.sha(before.encode())==row['beforeSha256']
        inverse(before,after,row['constants']);tokens+=len(raw(before))
        methods=re.findall(r'@Test\s+(?:@DisplayName\([^\n]*\)\s+)?void (\w+)\(',before)
        assert len(methods)==COUNTS[Path(row['path']).stem]
        catalog.extend(dict(path=row['path'],method=m) for m in methods)
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1) if 'assertEquals(' in after else after.replace('assertArrayEquals(','assertFalse(',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-fixture"'),1)])
        c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1]
        bads.append(after[:m.start()]+'"wrong-reference"'+after[m.end():])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('modified source oracle accepted')
    assert negatives==30 and len(catalog)==18
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=18,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
