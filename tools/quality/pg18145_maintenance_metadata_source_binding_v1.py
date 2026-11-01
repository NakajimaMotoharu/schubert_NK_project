"""Bind three plain metadata Sources, not actual filesystem/DB/run ownership."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18145-maintenance-metadata-source-binding-v1'
RECORDS=[["PG18129-maintenance-metadata-review-v1","fa13efd5616c210f3c378c6367e7a99ff164465b02ac384a9ccc45f2d63fb2ce"],["PG18130-maintenance-metadata-six-pt-v1","d5c3cc6557365d35a39ea7dcbd37fe8f97b93d6ae8c1a71a350ee1a179ca193f"],["PG18132-maintenance-metadata-six-post-v1","9482ca586c0e9195ee4b57fca1984e3e9d32d150cefe2e04fa67a04f3c909fa0"],["PG18134-maintenance-metadata-six-independent-v1","1efdc0be21f476ef8f70f07a0d0af3fbe125b40f7091eb359c3615ac59fe1854"],["PG18138-current2895-maintenance-metadata-registry-v1","051b650cdcecbf61bf14635c0303b27cb96a640328674c362a4bef522365513f"],["PG18140-current2895-maintenance-metadata-registry-post-v1","dfd2b6ad3e7e04e8b731cb3e6bd024a82b43441e6bd7870b575a7bedb7833180"],["PG18142-current2895-maintenance-metadata-wbs-v1","d296c5a82c4b4a488a03bbc8491e0aa9467b30bcaecc6939cea231fb73ca0d90"],["PG18144-current2895-maintenance-metadata-wbs-post-v1","40063e9b49192d599c86b7f10047c928f6e5d58b519d9e59eb1c24d387d2f28d"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2895,435,224,3050,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(3,616,1053,316,465,197,214)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=3,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=1,newQualityCases=6,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,jdkNamedTimeZoneInitializationInvoked=True,jdkTimezoneProviderCallsAndResourceReads=None,businessDateConversionInvoked=False,actualFilesystemOrOsOwnershipCertified=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
