"""Independent original16 inverse, including exact prefix order and34 negative metadata vectors."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11762-jdbc-collector-literal-source-post-v1'
PIN='18595a88e2013ad1724526cc3947fdc027958da2737ad23f83189549e53cb954'

def inverse(before,after,row):
    ts=canonical(after)
    for c in row['constants']:
        remove(ts,canonical('private static final String '+c['name']+' = '+c['literal']+';'))
        if ts.count(c['name'])!=c['references']:raise ValueError('all original fixed fixture references required')
        raw=canonical(c['literal']);assert len(raw)==1;ts=[raw[0] if t==c['name'] else t for t in ts]
    if row['assignmentExtracted']:
        expression='registry.get("nk_async_jobs").tag("state", state).gauge().value()'
        block=canonical('{ ++count; assertEquals(count, '+expression+'); }');matches=[i for i in range(len(ts)) if ts[i:i+len(block)]==block]
        if len(matches)!=1:raise ValueError('one extracted prefix increment immediately before original assertion')
        i=matches[0];ts[i:i+len(block)]=canonical('assertEquals(++count, '+expression+');')
    if ts!=canonical(before):raise ValueError('original independent oracle, boundary, deadline or operation order changed')

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG11760-jdbc-collector-literal-plan-v1/manifest.json';plan=data.read_checked(p,PIN);normal=data.read_checked(data.BASE/'PG11734-mq-recorder-literal-six-compile-v1/manifest.json','7d0f5f532b32896695e553c7ae886cdfef02595cbeb3c54c85c78b95b541505b');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['stringConstants']==13 and plan['stringReferences']==98 and plan['extractedPrefixAssignments']==1
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row);bads=[after.replace('@Test','@Disabled',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
        c=row['constants'][0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():])
        needle='release.await(5, TimeUnit.SECONDS)';assert after.count(needle)==1;bads.append(after.replace(needle,'release.await(4, TimeUnit.SECONDS)',1))
        if row['assignmentExtracted']:
            assert after.count('++count;')==1;bads += [after.replace('++count;','--count;',1),after.replace('++count;','',1)]
        assert len(re.findall(r'@Test\s+void ',before))==8
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row)
            except ValueError:negatives+=1
            else:raise AssertionError('changed independent fixture/oracle/deadline accepted')
    assert negatives==34;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=13,stringReferences=98,extractedPrefixAssignments=1,originalMethods=16,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
