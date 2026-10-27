"""Bind same-source20 pure claim PT, four fixes and retained raw5, without full quality credit."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='4749755f2562bd4e51658d8083a61e210ad2c521'
OUT=data.BASE/'PG12610-public-claim-completion-v1'
PINS={
    'normal':('PG12592-public-claim-six-compile-v1','11866f6596012549a85e43d0ff9a0b9577f446dccb00ff9ecaeadce127d1e305'),
    'host':('PG12594-public-claim-host-v1','a0f33528034e6296fa92ff228744a96d039139341a060710adf01ec18c260d00'),
    'post':('PG12598-public-claim-post-v1','e3eaf051b3be8e0e2b79e41a53fb7073258c60e0cfff922aa5d5237af6512f65'),
    'context':('PG12600-public-claim-context-v1','9b7488a8dc73b398b0be7f6c0f3c63f32d5a5b4e67a58d2d3026af418bec7d25'),
    'contextPost':('PG12602-public-claim-context-post-v1','d14bb76bcb5e73a048f61040e20c0cafd7aca449f54eb65a1cc9bf8268ceb6df'),
    'trace':('PG12604-public-claim-trace-v1','4143c2026cd2359535cebc2ee58f24594fb68450f08bcf1b46b23b7105c2defd'),
    'tracePost':('PG12605-public-claim-trace-post-v1','c644ab14768c7144776d669d72a0aac3bad54a407def5c52bf68ca848871a696'),
    'delta':('PG12606-current-public-claim-delta-v1','253591d4ff681d42f8729bb3f74de269f7b05e90155555208a9aac24b7e7cf4b'),
    'deltaPost':('PG12608-current-public-claim-delta-post-v1','25fe3fd3abd89e9f5fabb94b5ee5d03edc55b27613887406901cc37b9e75bb52')}


def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    values={k:data.read_checked(data.BASE/name/'manifest.json',digest) for k,(name,digest) in PINS.items()};n,h,p=(values[k] for k in ['normal','host','post'])
    assert n['testsExecuted']==0 and h['observedTestExecutions']==p['observedTestExecutions']==20 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==3 and p['otherTestPhysicalUnchanged']==1959 and p['forbiddenProbeHits']==p['frameGuardNativeMethodsExecuted']==0
    st=data.read_checked(data.BASE/'PG12596-public-claim-static-v1/manifest.json','ec931c42c87e54d25e8564e7dad14f117807d89dc6efe5f95601bdbf8dc0d0aa');assert st['source']==SOURCE and st['actualExit']==1 and st['reports']['pmd']['findings']==5 and st['reports']['checkstyle']['findings']==0
    assert values['context']['sourceContexts']==5 and values['contextPost']['metadataNegativeVectors']==22
    assert values['delta']['sourceDerivedRaw']==8507 and values['deltaPost']['totalPriorCorrections']==910
    assert values['tracePost']['oldRowsChangedShaOnly']==3 and values['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    plan=data.read_checked(data.BASE/'PG12590-public-claim-plan-v1/manifest.json','b2f729a14961d7d0ae65185840764c973ce71fb6ca9b60ee8825abb3fda2a224')
    assert plan['metadataNegativeVectors']==14 and plan['literalReferences']==16 and plan['allMainAndOtherInputsUnchanged']
    assert all(n['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges'])
    basic={name:v for name,v in p['directBatchClasses'].items() if name.rpartition('/')[2] in ['BackupWorkerRequest.class','BackupWorkerRequest$Verification.class','CleanupWorkerRequest.class']}
    assert len(basic)==3
    totals={kind:dict(missed=sum(v['counters'][kind]['missed'] for v in basic.values()),covered=sum(v['counters'][kind]['covered'] for v in basic.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
    assert totals==dict(LINE=dict(missed=0,covered=99),METHOD=dict(missed=0,covered=14),CLASS=dict(missed=0,covered=3),BRANCH=dict(missed=0,covered=88))
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2356_公開claim三Test四同値是正_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2357_公開claim三Test四同値是正_製造単体結果.md';supplement=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2358_公開claim三Test_仕様・分母補足.md'
    assert not list(Path(h['begin']['testCwd']).iterdir())
    verify(invocation);OUT.mkdir();value=dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=20,suites=3,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),specificationSupplementPath=str(supplement.relative_to(data.ROOT)),specificationSupplementSha256=data.sha(supplement.read_bytes()),relatedBugs=['BUG1986'],relatedYkt=['YKT1734'],implementationDecision='PG-D749',allMainClassesUnchanged=1843,changedTestPhysical=3,allOtherTestPhysicalUnchanged=1959,selectedBasicThreeCounters=totals,directBatchClasses=p['directBatchClasses'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=5,staticActualExit=1,sourceRawCorrections=4,sourceDerivedRaw=8507,totalCorrections=910,oldContextRebindings=5,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
