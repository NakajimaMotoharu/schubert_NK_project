"""Independent full16 token inverse with unequal declaration/value/reference/oracle/deadline negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from pg11208_web_supplied_metric_fixture_source_post import inverse as string_inverse
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11832-mq-media-collector-value-source-post-v1'
PIN='91285e0291b3636247a2e37209dbd6cd44064c6bec1cd82bd9aa448e428ad0ea'

def inverse(before,after,rows):
    tokens=canonical(after);row=next(r for r in rows if r['kind']=='ORDER_INT');remove(tokens,canonical('private static final int '+row['name']+' = '+row['literal']+';'))
    if tokens.count(row['name'])!=1:raise ValueError('one exact read/publication condition')
    tokens=[row['literal'] if t==row['name'] else t for t in tokens];string_inverse(before,' '.join(tokens),[r for r in rows if r['kind']=='STRING'])

def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11830-mq-media-collector-value-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG11804-job-outbox-value-literal-six-compile-v1/manifest.json','cfa574ea833d73ee31adfb96fba25fb5909890a2fb1fe32413049618b4ca58ea');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['stringConstants']==9 and plan['orderConstants']==2
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants']);assert len(re.findall(r'@Test\s+void ',before))==8
        bads=[after.replace('@Test','@Disabled',1)]
        sr=[r for r in row['constants'] if r['kind']=='STRING']
        for c in sr:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
        c=sr[0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():])
        c=next(r for r in row['constants'] if r['kind']=='ORDER_INT');decl='private static final int '+c['name']+' = '+c['literal']+';';occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1]
        bads += [after.replace(decl,decl.replace(c['literal']+';','3;'),1),after.replace(decl,'',1),after[:occ.start()]+'3'+after[occ.end():]]
        needle='latch.await(5, TimeUnit.SECONDS)' if 'MqPressure' in row['path'] else 'gate.await(5, TimeUnit.SECONDS)';assert after.count(needle)==1;bads.append(after.replace(needle,needle.replace('5,','4,'),1))
        needle='i < 64' if 'MqPressure' in row['path'] else 'index < 64';assert after.count(needle)==1;bads.append(after.replace(needle,needle.replace('64','63'),1))
        total=36 if 'MqPressure' in row['path'] else 3;needle=f'assertEquals({total}, registry.getMeters().size());';assert after.count(needle)>=1;bads.append(after.replace(needle,f'assertEquals({total-1}, registry.getMeters().size());',1))
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed independent fixture/oracle/deadline accepted')
    assert negatives==34;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=9,stringReferences=plan['stringReferences'],orderConstants=2,comparisonReferences=2,originalMethods=16,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
