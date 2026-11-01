"""Bind three complete pure menu Sources with Current/UI oracle, not real HTTP or DB."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18125-menu-projection-source-binding-v1'
RECORDS=[["PG18109-menu-projection-review-v1","3c65558e6d9aa80b067ae46482f99226b82178e86a15b172afba9205547e3649"],["PG18110-menu-projection-six-pt-v1","583af92a0abdd4662e31b9ee272a2b7b541946f49abcca5515e82b31848a8482"],["PG18112-menu-projection-six-post-v1","859fbe9fb8fafc38073c41be501f0c184ec95db4a91dadac3470e555c18c513b"],["PG18115-menu-projection-six-independent-v2","fea19390a1d0a85be60518b8d922f4f149f5ba6a1cb0fec41ca774239f0bf524"],["PG18118-current2889-menu-projection-registry-v1","3cd4ab994fd60df80022a48d3c6095c36a073ae470d603886a325348aaa0433d"],["PG18120-current2889-menu-projection-registry-post-v1","62edf46f50496d03234ad3f6f5f71125682bec856351861aa34d2a8d847c979b"],["PG18122-current2889-menu-projection-wbs-v1","df2342fdeaba7449be2153602ce8079632630b67501e6b0d2480e1b9939477f4"],["PG18124-current2889-menu-projection-wbs-post-v1","c6e19113cb2d915de58d4168c76fe04936ccf47f33b462cc007867ed0a95e7ce"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2889,434,223,3044,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(3,613,1050,314,463,196,213)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=3,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=1,newQualityCases=6,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualAuthenticationOrSessionIssued=False,actualHttpOrBrowserInvoked=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
