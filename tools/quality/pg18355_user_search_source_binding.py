"""Bind independent whole User search form evidence, without execution replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18355-user-search-source-binding-v1'
RECORDS=[["PG18339-user-search-form-review-v1","8e523784a073b3ac4666cbb9f5506a4aeef85775351374298fdb8ca7ae24ef4a"],["PG18340-user-search-form-twelve-pt-v1","df3fbed9e58662eebdcbd2cc93634879d168b081fbd78dfe9210797a4a329d8b"],["PG18342-user-search-form-twelve-post-v1","b2e58e47102d412d28a1a1fc3ef7bf07fe1edca3ca94ff49a0c152563c38a594"],["PG18344-user-search-form-twelve-independent-v1","5f3c52b5292f466ccd3cde6de0a1e9597cd55c1598e654c6fb2713e12556a393"],["PG18348-current2976-user-search-registry-v1","b8906f29f42b0fb00d358003843fc7ba531c752f4653c0221bb8f300b016eab7"],["PG18350-current2976-user-search-registry-post-v1","bd473b34853e88718dd738683a53f912bb90cc5a123acdd46c5f7a7eb62f8d91"],["PG18352-current2976-user-search-wbs-v1","dbd2d3812f523960c01342d825366fb73df02581bc58c3d621f6ae08fecfce12"],["PG18354-current2976-user-search-wbs-post-v1","191d488b9210563dcf8d6afe6c38a606bb6702f50623241b675968ad7c7c3b25"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2976,448,234,3131,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(1,647,1090,200,331,483,213,233)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=1,newProductionFiles=0,newFour100Sources=1,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=12,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
