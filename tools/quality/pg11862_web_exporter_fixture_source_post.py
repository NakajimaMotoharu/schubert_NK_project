"""Independent all48 token inverse; 34 unequal fixture/owner/declaration/field-binding negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11208_web_supplied_metric_fixture_source_post import inverse as string_inverse
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11862-web-exporter-fixture-source-post-v1'
PIN='7ea994fe2c7b0005d833a1b97c04d2be517973c0ccaa7811a17f12b058ca7516'

def inverse(before,after,rows,gauge):
    tokens=canonical(after)
    if gauge:
        if tokens.count('suppliedReading')!=3:raise ValueError('exact field declaration/assignment/return binding required')
        tokens=['value' if t=='suppliedReading' else t for t in tokens]
    string_inverse(before,' '.join(tokens),rows)

def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11860-web-exporter-fixture-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG11834-mq-media-collector-value-six-compile-v1/manifest.json','878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==3 and plan['stringConstants']==11 and plan['fieldBindingTokensRenamed']==3
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();gauge='Gauge' in row['path'];assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants'],gauge);assert len(re.findall(r'@Test\s+void ',before))==16
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertFalse(source.isClosed());','assertTrue(source.isClosed());',1)]
        assert bads[1]!=after
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
        c=row['constants'][0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():])
        if gauge:
            occurrences=[m for m in LEX.finditer(after) if m.group()=='suppliedReading'];assert len(occurrences)==3
            for m in occurrences:bads.append(after[:m.start()]+'foreignReading'+after[m.end():])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'],gauge)
            except ValueError:negatives+=1
            else:raise AssertionError('changed independent fixture/oracle/owner binding accepted')
    assert negatives==34;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=11,stringReferences=plan['stringReferences'],fieldBindingTokensRenamed=3,originalMethods=48,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
