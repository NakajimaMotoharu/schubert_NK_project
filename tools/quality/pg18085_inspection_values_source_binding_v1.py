"""Bind four immutable inspection Source contracts, not actual SQL or parent completion."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18085-inspection-values-source-binding-v1'
RECORDS=[["PG18069-inspection-values-review-v1","261aab827248173e33d2aa7d169a5e0d221f51128225786f72e3815fb6b4e7c9"],["PG18070-inspection-values-eight-pt-v1","7802774d2f47e24cb045778a2a4e059bc6904de289463aa70d5887fbd39865cb"],["PG18072-inspection-values-eight-post-v1","08873076a2432f6734fa5e28fca094ad4adda0b7b84aedeafa4751b114d1e439"],["PG18074-inspection-values-eight-independent-v1","8d77bb1424cd3f2650b3c8d23f709d3f0efedaa9bd3adffd785b116b431d2a60"],["PG18078-current2871-inspection-values-registry-v1","8ad7ee8443c1b439de4afaec3832ed534511b37a4c6e8016b85f026ed8c6fdb7"],["PG18080-current2871-inspection-values-registry-post-v1","0ffd1fac542ef27f6ad6788b4ac1b344b10c268aaa9028749c926ca03b2fb602"],["PG18082-current2871-inspection-values-wbs-v1","8a28090ef0ba4c74378a925623087186873a019f4b469902ea126ca507e1c2d0"],["PG18084-current2871-inspection-values-wbs-post-v1","86dfd92116f1b8ae6713ff6caa5cd568efb60f289f25ac66dad7163c7d74bb70"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2871,432,221,3026,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'])==(4,601,1036,307,454,191)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=4,newProductionFiles=0,newFour100Sources=4,newQualityCases=8,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualInspectionExecutorInvoked=False,actualProcessSuccessCertified=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
