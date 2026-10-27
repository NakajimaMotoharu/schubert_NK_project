"""Independent full24 token inverse; declaration/value/reference/oracle/deadline negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from pg11208_web_supplied_metric_fixture_source_post import inverse as string_inverse
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11802-job-outbox-value-literal-source-post-v1'
PIN='bde68c853c70a3c82b9b35186b84e99019af09fd1549919dbc6ddd6db76abe1e'

def inverse(before,after,rows):
    tokens=canonical(after);remove(tokens,canonical('private static final int FAILURE_REGISTRATION_ORDINAL = 2;'))
    if tokens.count('FAILURE_REGISTRATION_ORDINAL')!=1:raise ValueError('one exact second-registration condition')
    tokens=['2' if t=='FAILURE_REGISTRATION_ORDINAL' else t for t in tokens];string_inverse(before,' '.join(tokens),[r for r in rows if r['kind']=='STRING'])

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG11800-job-outbox-value-literal-plan-v1/manifest.json';plan=data.read_checked(p,PIN);normal=data.read_checked(data.BASE/'PG11764-jdbc-collector-literal-six-compile-v1/manifest.json','a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==3 and plan['stringConstants']==10 and plan['stringReferences']==73 and plan['orderConstants']==3
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants'])
        bads=[after.replace('@Test','@Disabled',1)];string_rows=[r for r in row['constants'] if r['kind']=='STRING']
        for c in string_rows:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
        c=string_rows[0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():])
        decl='private static final int FAILURE_REGISTRATION_ORDINAL = 2;';occ=[m for m in LEX.finditer(after) if m.group()=='FAILURE_REGISTRATION_ORDINAL'][-1]
        bads += [after.replace(decl,decl.replace('2;','3;'),1),after.replace(decl,'',1),after[:occ.start()]+'3'+after[occ.end():]]
        limit='.range(0, 64)' if 'AsyncJob' in row['path'] else 'i < 64';wrong='.range(0, 63)' if 'AsyncJob' in row['path'] else 'i < 63';assert after.count(limit)==1;bads.append(after.replace(limit,wrong,1))
        total=5 if 'AsyncJob' in row['path'] else 3;needle=f'assertEquals({total}, registry.getMeters().size());';assert after.count(needle)>=1;bads.append(after.replace(needle,f'assertEquals({total-1}, registry.getMeters().size());',1))
        assert len(re.findall(r'@Test\s+void ',before))==8
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed independent fixture/oracle/deadline accepted')
    assert negatives==41;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=10,stringReferences=73,orderConstants=3,comparisonReferences=3,originalMethods=24,relatedUnchangedGeneratedMethods=4,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
