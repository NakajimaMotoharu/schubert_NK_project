"""Close only this whole9 host group, three corrections and retained raw4; not whole quality."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='917f2e755d4912e522b9893e55aa272fd8e80934'
OUT=data.BASE/'PG12660-run-session-completion-v1'
PINS={
 'normal':('PG12642-run-session-six-compile-v1','9444de936bee333dcc73a34419b26213a423a4ef02ea8be5e984d3612b12b629'),
 'host':('PG12644-run-session-host-v1','81f0c972f80df2ceb7f0e1fe796b0f71c1756a752e42df81920efaf9246cf323'),
 'post':('PG12648-run-session-post-v1','ae842806398dcd99f061b059abf4930e837553995574fe60ab191b8b7a0b6530'),
 'context':('PG12650-run-session-context-v1','554fd03716bf2f8ba8e2f34cb857284161be0c1dd8bb6e99939ffe839b4eb80d'),
 'contextPost':('PG12652-run-session-context-post-v1','cf24df3cdfba2e31863c32225969d098506253098043ca910f5388b42781e90e'),
 'trace':('PG12654-run-session-trace-v1','7655027cfe3709cc90b9407f4b836f356ae6239f1cadaf555953f393d982ccb5'),
 'tracePost':('PG12655-run-session-trace-post-v1','8854d6157a6b690b62677775ed4fa554174c716e61674cc013afe821c085ca2c'),
 'delta':('PG12656-current-run-session-delta-v1','60a0b6efb5d3122565580089250938b9d91c1310da80184ecda6449789911e30'),
 'deltaPost':('PG12658-current-run-session-delta-post-v1','81eb9ccb2f9c5fd849f33536d20d15f772176e4e7fba5355e04e501b2768d574')}

def main():
 invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',h) for name,h in PINS.values()],SOURCE)
 v={k:data.read_checked(data.BASE/name/'manifest.json',h) for k,(name,h) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
 assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==9 and not h['oldExecUnion']
 assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
 assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==2 and p['otherTestPhysicalUnchanged']==1960 and p['forbiddenProbeHits']==0
 run=p['directRunSessionClasses']['dev/codex/schubert/nk/batch/platform/InspectorRunEnvironment.class']['counters']
 assert run==dict(LINE=dict(missed=0,covered=7),METHOD=dict(missed=0,covered=2),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=2))
 codec=p['directRunSessionClasses']['dev/codex/schubert/nk/web/session/SessionAttributeCodec.class']['counters']
 assert codec['LINE']==dict(missed=15,covered=98) and codec['BRANCH']==dict(missed=7,covered=35)
 static=data.read_checked(data.BASE/'PG12646-run-session-static-v1/manifest.json','57f4f368562af361b544c8bd12504ac80f3f8f180412050b688ca286ee66f457')
 assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==4 and static['reports']['checkstyle']['findings']==0
 assert v['context']['sourceContexts']==4 and v['contextPost']['metadataNegativeVectors']==22 and v['delta']['sourceDerivedRaw']==8501 and v['deltaPost']['totalPriorCorrections']==916
 assert v['tracePost']['oldRowsChangedShaOnly']==2 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
 plan=data.read_checked(data.BASE/'PG12641-run-session-plan-v2/manifest.json','63f14299fff1e3e3ed7c267affe50aaf7e83986cb80923be5af0270f32251ec4')
 assert plan['metadataNegativeVectors']==13 and plan['totalReferences']==16 and plan['allMainAndOtherInputsUnchanged']
 failed=data.BASE/'PG12640-run-session-plan-failure-v1/manifest.json';failure=__import__('json').loads(failed.read_bytes())
 assert failure['actualExit']==1 and not failure['patchApplied'] and failure['productTestsExecuted']==0 and data.sha((data.ROOT/'tools/quality/pg12640_run_session_plan.py').read_bytes())==failure['entrySha256']
 docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2362_run環境SessionV2三役割命名_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2363_run環境SessionV2三役割命名_製造単体結果.md']}
 assert not list(Path(h['begin']['testCwd']).iterdir())
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=9,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,failedToolManifestSha256=data.sha(failed.read_bytes()),relatedBugs=['BUG1989','BUG1990'],relatedYkt=['YKT1737','YKT1738'],implementationDecision='PG-D751',allMainClassesUnchanged=1843,changedTestPhysical=2,allOtherTestPhysicalUnchanged=1960,selectedRunByteCounters=run,directRunSessionClasses=p['directRunSessionClasses'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=4,staticActualExit=1,sourceRawCorrections=3,sourceDerivedRaw=8501,totalCorrections=916,oldContextRebindings=4,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=1,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
