"""Bind three first-measured existing DTO/catalog Sources, no new production code or authorization."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18025-admin-values-source-binding-v1'
RECORDS=[["PG18009-admin-values-catalog-review-v1","b358067e698c6d186f6cb543ad295a0c8ac34878f1eba1fe9f66fe2b6bd06f9f"],["PG18010-admin-values-catalog-six-pt-v1","95aa7e6ac4c225813021a0813f8e89fb90783f42c353fa1ca09e4bed434e27bb"],["PG18012-admin-values-catalog-six-post-v1","9df1a1f9c0bc5bb34f94e1cb756c4a59821f05d244acb9bacff7526acdae3ad0"],["PG18014-admin-values-catalog-six-independent-v1","4aeef1a47b73f45341a5a806e14791eb3af091157553b4e75ff2cd1bca14fd07"],["PG18018-current2858-admin-values-registry-v1","401f67ec8f09c5604dd7341d042668bed9aa6efffff1419457e35cdf736a18c2"],["PG18020-current2858-admin-values-registry-post-v1","65286d705111aadd1b0297873811e08e1d1661f47e345be986c166e02c6909b8"],["PG18022-current2858-admin-values-wbs-v1","e2871bef569fadf736f38e2f6b68494eb2436019688c1de3ce701e3cce4b7ebd"],["PG18024-current2858-admin-values-wbs-post-v1","5c87dd3589f736fd78f7ec4fafd7c4eb6f0dc7532b477b8dd4c7e18f0402020e"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert m['tests']==2858 and m['totalMethodExecutions']==3013 and m['totalRepeatedOriginalMethods']==155 and m['necessaryJointRepeatedMethods']==71 and len(m['jointQualificationReferences'])==7
    assert m['sourceProgramDelta']==3 and m['measuredSourcePrograms']==591 and m['four100SourcePrograms']==299 and m['naturalZeroBranchSourcePrograms']==189 and m['incompleteSourcePrograms']==80
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=3,newProductionFiles=0,newFour100Sources=1,newThreeCounter100NaturalBranchZeroSources=2,newQualityCases=6,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualAdminMutationOrAuthorization=False,actualProviderInvoked=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
