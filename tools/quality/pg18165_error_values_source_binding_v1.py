"""Bind source/run qualified pure error classification; no actual MVC certificate."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18165-error-values-source-binding-v1'
RECORDS=[["PG18149-error-values-review-v1","ce20fa3cd823eeb75764751f363a5b1badf0c74504637d85e3d53c9812b2a4f2"],["PG18150-error-values-six-pt-v1","0a749071fac40dc09eb3522eabb2b99f61d1242f65c12c6029ad52f8bb5c4b15"],["PG18153-error-values-six-post-v2","3a84becad5b52c30a5ab69da2ba33023af4d01b66ab9f62116152f9d344c747a"],["PG18154-error-values-six-independent-v1","d9c4fe41b0e378293a85e4b72331370a7250d9f92e9f87216654ebd8d6ad07e1"],["PG18158-current2901-error-values-registry-v1","6977565eaecd085346ce980d7326849d3c0863f6660e423cea66ff9a45d766a8"],["PG18160-current2901-error-values-registry-post-v1","abf38c6af69200e0a7640a7884d1c978ecfadb6be0cbf60fe5fde065b50e6e2d"],["PG18162-current2901-error-values-wbs-v1","c102cdd383755b46bd7b1d8bc4e32b37aa856c77ab7519669e5e10c9cc5f130a"],["PG18164-current2901-error-values-wbs-post-v1","d449a4ef865d3dbd283dac5634cb247c9813f9e2b37b68b4b96d09225c3dca99"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2901,436,225,3056,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(3,619,1058,318,468,198,216)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=3,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=1,newQualityCases=6,newOrdinaryCases=0,officialFilteredSyntheticCodePhysicalClasses=1,NoCodeClassificationForGeneratedSwitch=False,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualHttpOrAuthenticationCertified=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
