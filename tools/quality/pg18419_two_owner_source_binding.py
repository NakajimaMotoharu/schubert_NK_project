"""Bind ownership correction proofs, not additional PT or formal acceptance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18419-two-owner-source-binding-v1'
RECORDS=[["PG18410-explicit-user-query-owner-v1","847c9b714d2da7d5ba12aac72298104f45940aa421b22ee0ff223b1258f5a128"],["PG18412-current3008-two-owner-correction-v1","48d59ab03dc8b6ae3ba9bbc2ebe9e9fc03dfc362485ec46449883fb4e3548d05"],["PG18414-current3008-two-owner-post-v1","d1e834cf1201b778273c287c130ad44e1831b4d9cd640be050ee63910c01c598"],["PG18416-current3008-two-owner-wbs-v1","ccaa1a0bc0f184f0e9f9778e927dabd46e9ff8094550af93c0b251993a701c81"],["PG18418-current3008-two-owner-wbs-post-v1","afbaa362019e5173e59248a2e4da7da3c38645d497701ba27f35a394f16f7468"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    refs=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[1][0]/'manifest.json',RECORDS[1][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(3008,451,236,3163,155)
    assert m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':238,'UNKNOWN':300}
    assert (m['newTestIds'],m['sourceProgramDelta'],m['uniqueProductMethodDelta'])==(0,0,0)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=refs,existingTestOwnersResolved=2,newBaselineOwners=0,newProductTests=0,newSourcePrograms=0,coverageExecUnion=False,oldRuntimeTransferred=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
