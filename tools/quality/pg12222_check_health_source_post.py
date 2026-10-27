"""Independent raw inverse of all8 pure checksum/health methods;31 malformed metadata/source vectors."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12222-check-health-source-post-v1'
PLAN='878a909ed94f2efd0fa8abe7178f4784d4dbb0a1ac6f1655c811b3952fdfae38'
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inverse(before,after,rows):
    tokens=raw(after)
    for row in rows:
        declaration=raw('private static final String '+row['name']+' = '+row['literal']+';')
        positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration]
        if len(positions)!=1:raise ValueError('one exact independent constant declaration required')
        i=positions[0];del tokens[i:i+len(declaration)]
        if tokens.count(row['name'])!=row['references']:raise ValueError('all exact independent references required')
        tokens=[row['literal'] if t==row['name'] else t for t in tokens]
    if 'if (reads++ == failAfter)' in before:
        declaration=raw('int readAttempt = reads; reads++; if (readAttempt == failAfter)')
        positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration]
        if len(positions)!=1:raise ValueError('capture old value, increment once before comparison/throw required')
        i=positions[0];tokens[i:i+len(declaration)]=raw('if (reads++ == failAfter)')
    if tokens!=raw(before):raise ValueError('all original raw oracle and method tokens required')
def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12220-check-health-plan-v1/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12194-audit-metric-six-compile-v1/manifest.json','971ee001e169f9fa05df627e0cd0789704518d952105c27328eabf86ebd4adff')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['stringConstants']==10 and plan['stringReferences']==76
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0;tokens=0;catalog=[]
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(after.encode())==row['sha256'] and data.sha(before.encode())==row['beforeSha256']
        inverse(before,after,row['constants']);methods=re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods)==4
        catalog.extend(dict(path=row['path'],method=m) for m in methods);tokens+=len(raw(before))
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-wire-fixture"'),1)])
        c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1]
        bads.append(after[:m.start()]+'"wrong-reference"'+after[m.end():])
        if row['readIncrementDecomposed']:
            assert after.count('reads++;')==1 and after.count('int readAttempt = reads;')==1
            bads.extend([after.replace('reads++;','',1),after.replace('reads++;','reads++; reads++;',1),after.replace('if (readAttempt == failAfter)','if (reads == failAfter)',1),after.replace('int readAttempt = reads;','int readAttempt = reads + 1;',1),after.replace('reads++;','reads--;',1)])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed oracle, wait, reference or disabled method accepted')
    assert negatives==31 and len(catalog)==8
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=8,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
