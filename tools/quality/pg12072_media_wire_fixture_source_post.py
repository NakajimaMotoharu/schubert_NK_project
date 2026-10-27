"""Independent raw inverse of all24 original methods;55 malformed metadata/source vectors."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12072-media-wire-fixture-source-post-v1'
PLAN='fff03dd5024b97ac3f481bd887834f9c62b0a52e78ddab1f77b85928a8b340fb'
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
    plan=data.read_checked(data.BASE/'PG12070-media-wire-fixture-plan-v1/manifest.json',PLAN)
    normal=data.read_checked(data.BASE/'PG12044-api-web-scrape-fixture-six-compile-v1/manifest.json','fe989f6495c165f388cd4cc916da0ea8ed6901420c61d7ada7e2a742f8e6b672')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==3 and plan['stringConstants']==23 and plan['stringReferences']==213
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0;tokens=0;catalog=[]
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(after.encode())==row['sha256'] and data.sha(before.encode())==row['beforeSha256']
        inverse(before,after,row['constants']);methods=re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods)==8
        catalog.extend(dict(path=row['path'],method=m) for m in methods);tokens+=len(raw(before))
        bads=[after.replace('@Test','@Disabled',1),after.replace('Duration.ofSeconds(2)','Duration.ofSeconds(3)',1)]
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
    assert negatives==55 and len(catalog)==24
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=24,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
