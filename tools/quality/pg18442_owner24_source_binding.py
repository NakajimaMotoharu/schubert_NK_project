"""Bind same-byte24 owner corrections, not any new PT or accepted scope."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18442-owner24-source-binding-v1'
RECORDS=[["PG18430-explicit-same-byte24-owner-preflight-v1","7117274b0623981b644cc3ae4413f14b460187a312ff07fbf30fb0e75f972d3e"],["PG18432-explicit-owner-rules24-qualified-v1","112780b531b6dfb6338c9a01a2841370ef7f69eae28895f363f93dd9e4d769ca"],["PG18434-current3008-owner24-correction-v1","598adca1e798cc76c586096744efd66337cd9c5c5b6e03382ec78503f3bfa1d3"],["PG18436-current3008-owner24-post-v1","f0f3039f0cf46f7682c9d26c94122bee0374c6901e77fe8230a6a489d01b51a1"],["PG18438-current3008-owner24-wbs-v1","d6d7c14acd25d96133fc14535d933633e3f71af165e38967cd2fc34cf1667198"],["PG18440-current3008-owner24-wbs-post-v1","9b5bed0d413c7a4d5950f9e12f629790217b46b46f35be51bba439b4e68ba4ea"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    refs=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(3008,451,236,3163,155)
    assert m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':262,'UNKNOWN':276}
    assert (m['newTestIds'],m['sourceProgramDelta'],m['uniqueProductMethodDelta'])==(0,0,0)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=refs,existingArtifactOwnerCandidatesResolved=24,existingMainOwnerCandidates=3,existingTestOrFixtureOwnerCandidates=21,newBaselineOwners=0,newProductTests=0,newSourcePrograms=0,coverageExecUnion=False,oldRuntimeTransferred=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
