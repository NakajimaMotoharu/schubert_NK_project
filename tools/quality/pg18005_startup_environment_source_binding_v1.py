"""Bind source-zero environment wrappers with branch N/A and disclosed public nonsecret digest."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18005-startup-environment-source-binding-v1'
RECORDS=[["PG17989-startup-environment-review-v1","dbfcf77be8df0cf31d34265c2c774fc6634f6e6de3a87357906916fdd286c2a1"],["PG17990-startup-environment-ten-pt-v1","0aaad556590d4bed0ac329b72eee78cbcbb64d24288e12a884b8cdbc036dc020"],["PG17992-startup-environment-ten-post-v1","7ab47d6e2acfdf8fd9da99c99d11884b0174b94cf001ea986c6f6fea3d20f4da"],["PG17994-startup-environment-ten-independent-v1","dab38e25f9b33aa6c5713859d271e415e44d60fb1e87875446f64260dae2f427"],["PG17998-current2852-startup-environment-joint-registry-v1","195e4b6338efc446e399c2d782dcf55257da2e378a41bff7d5b29dba66b628a6"],["PG18000-current2852-startup-environment-joint-registry-post-v1","16512072689eb269e54c1027eb4279eae201f64396a52f94f59f2266af7bc7d0"],["PG18002-current2852-startup-environment-joint-wbs-v1","41293e002cf2f14eac0898920008c360c0bac1a9fadcdd8cfcc93fe369b77f9e"],["PG18004-current2852-startup-environment-joint-wbs-post-v1","322b9cf74838109d2e19507aedaa5aaa876a37e75f196b7d2e1910cb79a52abc"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1]);p=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    names=['dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs','dev/codex/schubert/nk/web/bootstrap/WebStartupInputs']
    assert all(m['fullSourceUnits'][n]['branchNaturallyZero'] is True and m['fullSourceUnits'][n]['four100'] is False and m['jointQualificationReplacedUnitHistory'][n]['branchNaturallyZero'] is False for n in names)
    assert m['tests']==2852 and m['totalMethodExecutions']==3007 and m['totalRepeatedOriginalMethods']==155 and m['necessaryJointRepeatedMethods']==71 and len(m['jointQualificationReferences'])==7
    assert m['four100SourcePrograms']==298 and m['naturalZeroBranchSourcePrograms']==187 and m['incompleteSourcePrograms']==80
    assert p['cryptoOrKeyOperationsInvoked'] is p['publicDigestOnly'] is True and p['actualSecretKeysLoaded'] is p['actualDescriptorAdoptionOrNativeIo'] is False
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,oldPartialProofsPreserved=2,newThreeCounter100NaturalBranchZeroSources=2,newFour100Sources=0,newQualityCases=2,necessaryOriginalRepeatedCases=8,newOrdinaryCases=0,publicNonsecretDigestOnly=True,actualSecretKeysLoaded=False,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
