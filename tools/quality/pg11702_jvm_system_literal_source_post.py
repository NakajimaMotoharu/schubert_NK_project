"""Independent full56 token inverse; declaration/value/reference/oracle/deadline negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from pg11208_web_supplied_metric_fixture_source_post import inverse as string_inverse
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11702-jvm-system-literal-source-post-v1'
PIN='918f9082cad60641a70506b143d3ac67da65401d48e9fbb922bddd331eb8ddf4'

def inverse(before,after,rows):
    tokens=canonical(after);remove(tokens,canonical('private static final int FIRST_BINDER_ORDER = 1;'))
    if tokens.count('FIRST_BINDER_ORDER')!=1:raise ValueError('one exact first-callback condition')
    tokens=['1' if t=='FIRST_BINDER_ORDER' else t for t in tokens];string_inverse(before,' '.join(tokens),[r for r in rows if r['kind']=='STRING'])

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG11700-jvm-system-literal-plan-v1/manifest.json';plan=data.read_checked(p,PIN);normal=data.read_checked(data.BASE/'PG11674-standard-composition-literal-six-compile-v1/manifest.json','15a6eeb057afdb021d0403af21625b84664c7df00c9da343954cfe02762a4ce1');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==4 and plan['stringConstants']==14 and plan['stringReferences']==100 and plan['orderConstants']==4
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants'])
        bads=[after.replace('@Test','@Disabled',1)];string_rows=[r for r in row['constants'] if r['kind']=='STRING']
        for c in string_rows:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
        c=string_rows[0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():])
        decl='private static final int FIRST_BINDER_ORDER = 1;';occ=[m for m in LEX.finditer(after) if m.group()=='FIRST_BINDER_ORDER'][-1]
        bads += [after.replace(decl,decl.replace('1;','2;'),1),after.replace(decl,'',1),after[:occ.start()]+'2'+after[occ.end():]]
        assert after.count('job.get(10, TimeUnit.SECONDS)')==1;bads.append(after.replace('job.get(10, TimeUnit.SECONDS)','job.get(9, TimeUnit.SECONDS)',1))
        total=256 if 'JvmMetricsTest' in row['path'] else 128;needle=f'assertEquals({total}, total.get());';assert after.count(needle)==1;bads.append(after.replace(needle,f'assertEquals({total-1}, total.get());',1))
        assert len(re.findall(r'@Test\s+void ',before))==14
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negatives+=1
            else:raise AssertionError('changed independent fixture/oracle/deadline accepted')
    assert negatives==56;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=14,stringReferences=100,orderConstants=4,comparisonReferences=4,originalMethods=56,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
