"""Bind pure Web log claim record; no proof of live lease or retry."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18395-weblog-claim-source-binding-v1'
RECORDS=[["PG18379-weblog-claim-review-v1","f1c5a0aea9a9ab5e78141d4ae738455625c75f3c1ca1f59deede4f55c810b26f"],["PG18380-weblog-claim-six-pt-v1","48d9c1c823c3baa5395c6568af60b51f0df1743c01d896c97552732a46861a92"],["PG18382-weblog-claim-six-post-v1","9db43a417108ef03b99763c892d720600b575ee85bef2266f5a2c208d2c3f6e8"],["PG18384-weblog-claim-six-independent-v1","901912dc265e58e2e3079275aebde4c2be0d5d89d0fc1d9fd8858b32b85a0773"],["PG18388-current3008-weblog-claim-registry-v1","f561fa5e450285c6811f195c5a68670f1ddd090ef8782ce2a0815e6b1766b2b6"],["PG18390-current3008-weblog-claim-registry-post-v1","a99dc83c54be418b7ee45846dae92f7e746a224ae30d6c885311d14507cd98f1"],["PG18392-current3008-weblog-claim-wbs-v1","4f2f4a6e9d4252a4b9ff9e4dde76632dbfd756b3f16a72ef6b41eb0bc9c8aefa"],["PG18394-current3008-weblog-claim-wbs-post-v1","34af060f02e0de34b66b591e4b13e6074efecd8095c22ddfa8cb7b567bf26980"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(3008,451,236,3163,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(1,650,1093,200,334,486,213,233)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=1,newProductionFiles=0,newFour100Sources=1,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=6,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
