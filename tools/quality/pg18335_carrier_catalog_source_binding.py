"""Bind clean v2 carrier scope; prior failed PT and metadata witness remain distinct."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18335-carrier-catalog-source-binding-v1'
RECORDS=[["PG18321-carrier-catalog-review-v2","81fc065a255f5d14626b69c015aeed984ea6839a308e5ffedb8cc2adeddc7231"],["PG18321-carrier-catalog-five-pt-v2","c7528850e8e914d93ea0e13cfadbca1fbfe42bf92ce93c478f586ee03d007815"],["PG18322-carrier-catalog-five-post-v1","1131d023445e6e2cd2fb62a7976b337ffe92b8c27a41cea975ae4fecad35923b"],["PG18324-carrier-catalog-five-independent-v1","60d67d701392914505d219e6a3d439b0dd2cbf165440ef76cae126069242e39b"],["PG18328-current2964-carrier-catalog-registry-v1","462e898663d60b1c68c54956fffe07e494472fa187a13b094ed44247d780705d"],["PG18330-current2964-carrier-catalog-registry-post-v1","f176bbb285be23ef754eab40208bc3953d83129ecb30244314ff9ef2a85c46c1"],["PG18332-current2964-carrier-catalog-wbs-v1","c048e3efb440ee99f0ced54b70d65633277d7ff6bc66882ea92cbea9157e8574"],["PG18334-current2964-carrier-catalog-wbs-post-v1","6481445a1a2b7fc6f5de8c30db9748baa1c9353011ff0aee0848835e986dab34"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2964,447,233,3119,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(4,646,1089,200,330,482,213,233)
    extra=[('PG18317-carrier-failure-preservation-v1','11a7f7a1a83a9bf5269cabd6ff0f81ed09dfcc90a6a995591799d8e193da6984'),('PG18318-composite-bytecode-witness-v2','83d17bd865a4269cc8f46f2a7c8e0fbf1e5dda42e700c479f9d2bf05be41a14c')]
    preservation_and_tool_only=bind([(data.BASE/n/'manifest.json',h) for n,h in extra],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,preservationAndToolOnlyBindings=preservation_and_tool_only,newMeasuredExistingProductionSources=4,newProductionFiles=0,newFour100Sources=0,newNaturalBranchZeroThreeCounterSources=4,newQualityCases=5,newOrdinaryCases=0,priorFailedGroupExit=1,priorFailedToolExit=1,necessaryUnqualifiedPriorSucceededMethodRepeats=4,failedResultsPromotedToPass=False,productTestsReexecutedByBinding=0,coverageExecUnion=False,queryNullCasesDynamicallyVerified=False,wholeQueryProgramAccepted=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
