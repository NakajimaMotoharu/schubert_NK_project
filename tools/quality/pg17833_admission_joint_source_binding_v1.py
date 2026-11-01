"""Bind same-source real-wait coverage and qualified quality/source ownership boundary."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17833-admission-joint-source-binding-v1'
RECORDS=[["PG17812-owned-admission-wait-runner-metadata-v1","37a07111990dc25b48fe87d7cc2666f937be69a8187e039b34efbf2c965186d7"],["PG17814-owned-admission-wait-environment-binding-v1","48970d3d33105beafbbcf775a06ba3f22ca31fa29f32a2951a52fc745212793d"],["PG17815-admission-actual-wait-review-v1","f685cf0c1fd4dedd085042d0ff0c2c98148493075d1049f8542f19b27f792b54"],["PG17816-admission-actual-wait-five-pt-v1","6eddd61a889e0ebb85a9f1eb3451ace5a272c803e1ee3b606cada04a21203f8e"],["PG17818-admission-actual-wait-five-post-v1","42a733fb6590631f6e6f52886a0a01853c036d9a167b28aeab0ea4e1267ab180"],["PG17820-admission-actual-wait-five-independent-v1","b272f023afdb5a5c0cc69904a9c20c7004d2e7cbb86bb7b074e0ff6c163eacd6"],["PG17825-current2827-admission-joint-registry-v2","8110527ffbaa8152c358418fab5b113f48ec2568bde424778766d2a66c395d2c"],["PG17827-current2827-admission-joint-registry-post-v2","b447111a774a3dc635937ec9f3a61b39153175714c53f1d8d054c3c3b70b1a1a"],["PG17830-current2827-admission-joint-wbs-v1","a3e60ec26722db2d0130190d2a961bcde8871d7f109954afc7b1f83c8fe10dec"],["PG17832-current2827-admission-joint-wbs-post-v1","2d9c084b410fbf216533852fa4316cea354f545c788bc26b71e83fd46c5a579e"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    old=data.read_checked(data.BASE/'PG17794-current2825-web-mvc-registry-v1/manifest.json','8aceaae95f920ed2be0304a68972a104f557a1ac24cfc89bfebf58f3bbc70dfe')
    new=data.read_checked(data.BASE/RECORDS[6][0]/'manifest.json',RECORDS[6][1]);q=data.read_checked(data.BASE/RECORDS[7][0]/'manifest.json',RECORDS[7][1])
    target='dev/codex/schubert/nk/web/bootstrap/WebHttpAdmission';quality='tools/quality/architecture/WebHttpAdmissionWaitingContractTest.java'
    assert new['owners']==old['owners'] and quality not in new['owners'] and q['qualityBoundaryNegativeVectors']==6
    assert new['jointQualificationReplacedUnitHistory'][target]==old['fullSourceUnits'][target]
    assert new['fullSourceUnits'][target]['four100'] is True and new['fullSourceUnits'][target]['postSha256']==RECORDS[4][1]
    assert data.sha((data.ROOT/quality).read_bytes())=='797e3809992d2e3b3a6aba9477b28e198970bd7c80a0c9f0519960f11b9deb78'
    failed={'pg17824_current2827_admission_joint_registry.py':'fee81e756ab0b027d2443551efc31b442d2cd2883ac9fd93d2fcb5d5277a642a','pg17826_current2827_admission_joint_registry_post.py':'1a3655d1bce52d4031821fae7ce6993ea84a21fe3869b1f30a4680cbe42dbd6a'}
    assert all(data.sha((data.ROOT/'tools/quality'/n).read_bytes())==h for n,h in failed.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,sourceOwnerRowsUnchanged=True,qualityToolReferenceNotCanonicalArtifact=True,qualityBoundaryNegativeVectors=6,failedEntriesPreserved=failed,allSuccessfulProductOrAnalyzerReplay=0,fullSourceReplacedInOneExec=True,oldPartialStoredInHistory=True,coverageExecUnion=False,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
