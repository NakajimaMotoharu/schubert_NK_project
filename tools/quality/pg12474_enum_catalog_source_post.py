"""Independent raw inverse of two complete independent enum methods;16 malformed metadata/source vectors."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12474-enum-catalog-source-post-v1'
PLAN='c0fb1d72f54e07805f66fa6571c2850ae42ce91e69b1f70aa258a46dbac08762'
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
    if tokens!=raw(before):raise ValueError('all original raw oracle and method tokens required')
def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12472-enum-catalog-plan-v1/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['stringConstants']==5 and plan['stringReferences']==25
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0;tokens=0;catalog=[]
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(after.encode())==row['sha256'] and data.sha(before.encode())==row['beforeSha256']
        inverse(before,after,row['constants']);methods=re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods)==1
        catalog.extend(dict(path=row['path'],method=m) for m in methods);tokens+=len(raw(before))
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-wire-fixture"'),1)])
        c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1]
        bads.append(after[:m.start()]+'"wrong-reference"'+after[m.end():])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed oracle, wait, reference or disabled method accepted')
    assert negatives==16 and len(catalog)==2
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=2,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
