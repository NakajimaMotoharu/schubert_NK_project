"""Bind latest-primary270 owner corrections; runtime/counters and formal acceptance unchanged."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18462-latest270-owner-source-binding-v1'
RECORDS=[["PG18450-latest-explicit270-owner-preflight-v1","d6df2f07c40985094c229bf407b47e3601a5253fca370c5d2b97a6fb8ccad769"],["PG18452-latest-primary-rules270-qualified-v1","1d29bf436618a1e0f5e7d488e40791b799239035d8a7bd1140fd6e88de3ff51a"],["PG18454-current3008-latest270-owner-correction-v1","0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51"],["PG18456-current3008-latest270-owner-post-v1","17fde5da39646600b827b3c3c86d251ed58b8983e0633586e96f235a1e4c6518"],["PG18458-current3008-latest270-owner-wbs-v1","7e825b330df6f2810ead4ae517c6dd71d3f12905e1ba3b1fc666bdf0e3704543"],["PG18460-current3008-latest270-owner-wbs-post-v1","3d532e99bb4b451774baf5e9cb82540261e6ff90686f46e83b16b32aa42c9b2b"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    refs=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(3008,451,236,3163,155)
    assert m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':532,'UNKNOWN':6}
    assert (m['newTestIds'],m['sourceProgramDelta'],m['uniqueProductMethodDelta'])==(0,0,0)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=refs,existingTestOwnerCandidatesResolved=270,originalQualificationFlagUnknownCount=5,qualificationOfThoseRecordsInferred=False,newBaselineOwners=0,newProductTests=0,newSourcePrograms=0,coverageExecUnion=False,oldRuntimeTransferred=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
