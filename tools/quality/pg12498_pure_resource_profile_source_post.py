"""Strict independent typed raw inverse for all33 changed original tests plus unchanged one companion; no folded literal equivalence."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12498-pure-resource-profile-source-post-v1'
PLAN='2afc6237ad922fab24e622ab94b8c9886518bcd742ec76041eb54a1c49f42f14'
COUNTS={'ResourceScopeTest': 8, 'FactoryResourceScopeTest': 18, 'FixedNativeCoverageProfileTest': 5, 'ObservationValueRedactionTest': 2}
NUMERIC_IDS={'PMD-06944', 'PMD-06947', 'PMD-07117', 'PMD-06946', 'PMD-06945', 'PMD-06943', 'PMD-07118'}
CHAR_IDS={'PMD-06943'}
STRING_IDS={'PMD-06942', 'PMD-04444', 'PMD-06937', 'PMD-06499', 'PMD-07116', 'PMD-06938', 'PMD-06936', 'PMD-06500'}

def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(before,after,rows):
    ts=raw(after)
    for row in rows:
        ident=row['id'];typ='char' if ident in CHAR_IDS else 'int' if ident in NUMERIC_IDS else 'String' if ident in STRING_IDS else None
        if typ is None or row['type']!=typ:raise ValueError('independent approved constant type/finding ID required')
        declaration=raw('private static final '+typ+' '+row['name']+' = '+row['literal']+';')
        positions=[i for i in range(len(ts)-len(declaration)+1) if ts[i:i+len(declaration)]==declaration]
        if len(positions)!=1:raise ValueError('one exact typed constant declaration required')
        start=positions[0];del ts[start:start+len(declaration)]
        if ts.count(row['name'])!=row['references']:raise ValueError('all exact original references required')
        ts=[part for token in ts for part in (raw(row['literal']) if token==row['name'] else [token])]
    if ts!=raw(before):raise ValueError('all original oracle/method/control/exception/concurrency tokens required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12496-pure-resource-profile-plan-v1/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==4 and plan['stringConstants']==8 and plan['numericConstants']==7 and plan['stringReferences']==48
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    assert {c['id'] for r in plan['sourceChanges'] for c in r['constants']}==NUMERIC_IDS|STRING_IDS
    negatives=0;catalog=[];tokens=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,row['constants']);tokens+=len(raw(before));methods=re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods)==COUNTS[Path(row['path']).stem]
        catalog.extend(dict(path=row['path'],method=m) for m in methods)
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1)]
        for c in row['constants']:
            decl='private static final '+c['type']+' '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1
            bad_literal='"wrong-fixture"' if c['type']=='String' else '99'
            wrong_type='Object' if c['type']=='String' else 'long' if c['type']=='int' else 'int'
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],bad_literal),1),after.replace(decl,decl.replace('final '+c['type']+' ','final '+wrong_type+' '),1)])
        c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1]
        bads.append(after[:m.start()]+'WRONG_REFERENCE'+after[m.end():])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed typed fixture/oracle accepted')
    assert negatives==57 and len(catalog)==33
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=33,additionalUnchangedCompanionMethods=1,expectedExecutedMethods=34,originalCatalog=catalog,originalRawTokens=tokens,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
