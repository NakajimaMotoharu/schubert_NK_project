"""Strict original28 raw inverse,21 String constants/one two-reference ordinal,53 negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12042-api-web-scrape-fixture-source-post-v1'
PIN='63a2eee4ac2062bb33b61922403de8c798b95160a1bf1efac0b53e5b2f82c173'
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def erase(tokens,declaration):
    positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration]
    if len(positions)!=1:raise ValueError('one exact independent declaration required')
    i=positions[0];del tokens[i:i+len(declaration)]
def inverse(before,after,rows):
    tokens=raw(after)
    for row in rows:
        if row['kind']!='STRING':continue
        erase(tokens,raw('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name'])!=row['references']:raise ValueError('all exact String references required')
        tokens=[row['literal'] if t==row['name'] else t for t in tokens]
    if any(r['kind']=='ORDER_INT' for r in rows):
        erase(tokens,raw('private static final int COUNTER_PROVIDER_KIND = 1;'))
        if tokens.count('COUNTER_PROVIDER_KIND')!=2:raise ValueError('two counter-choice if references required')
        tokens=['1' if t=='COUNTER_PROVIDER_KIND' else t for t in tokens]
    if tokens!=raw(before):raise ValueError('all original28 fixture/oracle/assertion/deadline tokens required')
def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG12040-api-web-scrape-fixture-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG12016-web-business-record-six-compile-v1/manifest.json','214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0;token_count=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants']);assert len(re.findall(r'@Test\s+void ',before))==14;token_count+=len(raw(before));strings=[r for r in row['constants'] if r['kind']=='STRING'];bads=[after.replace('@Test','@Disabled',1)]
        for c in strings:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-fixed-vector"'),1)]
        c=strings[0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:m.start()]+'"wrong-reference"'+after[m.end():]);assert 'job.get(10, TimeUnit.SECONDS)' in after;bads.append(after.replace('job.get(10, TimeUnit.SECONDS)','job.get(9, TimeUnit.SECONDS)',1));n='900' if 'ApiMetric' in row['path'] else '2219';assert 'assertEquals('+n+',' in after;bads.append(after.replace('assertEquals('+n+',','assertEquals(1,',1))
        if any(r['kind']=='ORDER_INT' for r in row['constants']):
            decl='private static final int COUNTER_PROVIDER_KIND = 1;';m=[m for m in LEX.finditer(after) if m.group()=='COUNTER_PROVIDER_KIND'][-1];bads += [after.replace(decl,'',1),after.replace(decl,decl.replace('= 1;','= 2;'),1),after[:m.start()]+'2'+after[m.end():]]
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed fixed literal/ordinal/oracle/deadline accepted')
    assert negatives==53;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=21,stringReferences=plan['stringReferences'],orderConstants=1,comparisonReferences=2,originalMethods=28,originalRawTokens=token_count,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
