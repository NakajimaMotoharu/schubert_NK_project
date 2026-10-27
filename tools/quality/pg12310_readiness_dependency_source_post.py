"""Independent strict raw inverse for all4 original methods; no literal folding or oracle edits."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg12222_check_health_source_post import inverse,raw

OUT=data.BASE/'PG12310-readiness-dependency-source-post-v1'
PLAN='9fab66c6a699e86346da415ae87c23bf384a05a00804bd96c4f86a711e401f23'
COUNTS=dict(ApiReadinessPredicateTest=3,WebRuntimeDependencyTest=1)

def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12308-readiness-dependency-plan-v1/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json','776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['stringConstants']==5 and plan['stringReferences']==29
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
    assert negatives==16 and len(catalog)==4
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=4,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
