"""Bind two independent search forms without executing Product again."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18375-qn-search-source-binding-v1'
RECORDS=[["PG18359-question-notification-search-review-v1","c47da74d145c9ce0dd7f96524686474294ac53ca15bd60dbbbcd4acc44e7d3a9"],["PG18360-question-notification-search26-pt-v1","6aa3a82b4c677591d963e0a170e64f3aa433242bc7549550649eae5d52ceb038"],["PG18362-question-notification-search26-post-v1","37517334dc95f2fa471bd820d6e24a3f497c4a8b6b55f63626684e9afcfff1ce"],["PG18364-question-notification-search26-independent-v1","5b537d900dc3223736eb1b2616355196dccaeb77791878205fb7ea3d09422384"],["PG18368-current3002-qn-search-registry-v1","a72db411c88562b44ff0de8b303d792f9b8ff81011169744644baa204389f65b"],["PG18370-current3002-qn-search-registry-post-v1","a184c5ba24294a7202f94cf87020e36cecbd87152ba3e81629f5f047f7a8b4eb"],["PG18372-current3002-qn-search-wbs-v1","3b758cd7867b0d796358b0c4444fa6f59d7bce617b7ef4f199a530c95d8f3975"],["PG18374-current3002-qn-search-wbs-post-v1","efc1ddfec89bf2a0a52034fdbd1da55e2508754b5723c426741518f50d5ad6be"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(3002,450,235,3157,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(2,649,1092,200,333,485,213,233)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=2,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=26,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
