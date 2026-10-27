"""Independent complete30-method inverse and16 meaningful negative source mutations; no product run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove

OUT=data.BASE/'PG11642-db-pool-binding-fatal-case-source-post-v1'
NAME='FATAL_SUPPLIER_CASE'
DECL='private static final int '+NAME+' = 1;'

def inverse(before,after):
    tokens=canonical(after);remove(tokens,canonical(DECL))
    if tokens.count(NAME)!=4:raise ValueError('exact four original fatal comparisons')
    tokens=['1' if t==NAME else t for t in tokens]
    if tokens!=canonical(before):raise ValueError('original independent assertions/fixtures/branches/owner/finite deadlines changed')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    p=data.BASE/'PG11640-db-pool-binding-fatal-case-plan-v1/manifest.json';plan=data.read_checked(p,'ba5be4b11c36cf931ed494b6d5765b3c64168f2781cc6fbebfe0e03fed15c86a')
    old=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    snapshot=Path(old['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2 and plan['integerConstants']==2 and plan['comparisonReferences']==8
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in old['begin']['inputHashes'].items() if p not in changed)
    negatives=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after)
        reference=[m for m in LEX.finditer(after) if m.group()==NAME][-1]
        bads=[after.replace(NAME+' = 1;',NAME+' = 2;',1),after.replace(DECL,'',1),
            after[:reference.start()]+'0'+after[reference.end():],after.replace('@Test','@Disabled',1),
            after.replace('assertEquals(4, registry.getMeters().size());','assertEquals(5, registry.getMeters().size());',1),
            after.replace('TimeUnit.SECONDS.toNanos(30)','TimeUnit.SECONDS.toNanos(29)',1),
            after.replace('workers.shutdownNow();','',1),after.replace('Thread.State.BLOCKED','Thread.State.WAITING',1)]
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad)
            except ValueError:negatives+=1
            else:raise AssertionError('changed original case/oracle/owner/deadline accepted')
    assert negatives==16
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=old['source'],invocation=invocation,planManifestSha256=data.sha(p.read_bytes()),sourceChanges=plan['sourceChanges'],integerConstants=2,comparisonReferences=8,
        allOriginalOracleTokensRestored=True,allOriginalGuardAndDeadlineTokensRestored=True,allMainAndOtherInputsPreserved=True,originalMethods=30,metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
