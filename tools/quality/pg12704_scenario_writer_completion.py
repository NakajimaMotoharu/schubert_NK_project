"""Bind original eight writer/verifier Tests and five corrections, keeping failure history and native HOLD."""
from pathlib import Path
import platform
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='e353b1f49a740a426031fdc199f7ce8b26081971'
OUT=data.BASE/'PG12704-scenario-writer-completion-v1'
PINS={
 'normal':('PG12686-scenario-writer-six-compile-v1','20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d'),
 'host':('PG12688-scenario-writer-host-v1','6c1805f0ee828d482aa89190460811c30514422beec074b2ff604214990caff8'),
 'post':('PG12693-scenario-writer-post-v2','65934c65ce4836ce0f3b50c109a21ce3d327418a5eef9fad6926cf4b5352b872'),
 'context':('PG12694-scenario-writer-context-v1','ffeadb4a1d3136f4b4fa9f3de29db1f4984add4900872cb2f2b0cef7e4a61415'),
 'contextPost':('PG12696-scenario-writer-context-post-v1','b2b8426c0078bc41d086ba0d7f1c4ff55b960ba9384df7928ce0c3a5355cfb6c'),
 'trace':('PG12700-scenario-writer-trace-v2','1a578401cdce20798948deeb8b30322a0d0a663a79ea5ce2b6a04abc983e877f'),
 'tracePost':('PG12701-scenario-writer-trace-post-v2','849ea1cbe34cf7d5f95087303449e1aab77f4fc9ed9de64365026c8ee12ce137'),
 'delta':('PG12702-current-scenario-writer-delta-v1','1015b4f3d941bbbaf5dd209512088985f87a19c665f63c375fcf49c412157df4'),
 'deltaPost':('PG12703-current-scenario-writer-delta-post-v1','25f13d394b1870502641b721a00e3690801b438611b7abca7b8f580de86b4f07')}

def main():
 invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',h) for name,h in PINS.values()],SOURCE)
 v={k:data.read_checked(data.BASE/name/'manifest.json',h) for k,(name,h) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
 assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==8 and not h['oldExecUnion']
 assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
 assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==2 and p['otherTestPhysicalUnchanged']==1960 and p['forbiddenProbeHits']==0 and p['ownedTempRootEmptyAfter'] and p['ownedTempIdentityUnchanged']
 assert len(h['begin']['eligibilityClosureSourceHashes'])==56 and len(p['extraReviewedSourceHashes'])==1 and len(p['directImportsBySource'])==59
 main={name:value for name,value in p['directWriterVerifierClasses'].items() if name.startswith('dev/codex/schubert/nk/api/')};assert len(main)==2
 totals={kind:dict(missed=sum(x['counters'][kind]['missed'] for x in main.values()),covered=sum(x['counters'][kind]['covered'] for x in main.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
 assert totals==dict(LINE=dict(missed=0,covered=50),METHOD=dict(missed=0,covered=7),CLASS=dict(missed=0,covered=2),BRANCH=dict(missed=0,covered=26))
 static=data.read_checked(data.BASE/'PG12690-scenario-writer-static-v1/manifest.json','17b8482c9fa40b627242b21a418ac385a925ecd66fe68ec57752ca7d0a666692')
 assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==2 and static['reports']['checkstyle']['findings']==0
 assert v['context']['sourceContexts']==2 and v['contextPost']['metadataNegativeVectors']==22 and v['delta']['sourceDerivedRaw']==8493 and v['deltaPost']['totalPriorCorrections']==924
 assert v['tracePost']['oldRowsChangedShaOnly']==1 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
 binding=v['trace']['currentScenarioWriterBinding']['sourceChanges'];assert len(binding)==1 and binding[0]['canonicalOwner']==binding[0]['canonicalCostOwner']=='WBS-P008-06'
 plan=data.read_checked(data.BASE/'PG12684-scenario-writer-plan-v1/manifest.json','71ae38137584d347696953a2ae460d1bb825a05a97dd1cbbb37ac794b4f58075');assert plan['metadataNegativeVectors']==16 and plan['finallyOwnerOnlyChange'] and plan['allMainAndOtherInputsUnchanged']
 failures={}
 for name,entry,digest in [('PG12692-scenario-writer-post-failure-v1','pg12692_scenario_writer_post.py','5daa15ff497aba63ebccfb70e3f8ecedeb9775251a1d9e41f6c9fdfd071a8d9a'),('PG12698-scenario-writer-trace-failure-v1','pg12698_scenario_writer_trace.py','bb1ede35feceedd04ea1ce43c41df6ef8b02366abe79047c0c642165ef69e8b5')]:
  f=data.BASE/name/'manifest.json';value=json.loads(f.read_bytes());assert value['actualExit']==1 and value['source']==SOURCE and value['productTestsExecuted']==0 and data.sha((data.ROOT/'tools/quality'/entry).read_bytes())==value['entrySha256']==digest;failures[name]=data.sha(f.read_bytes())
 temp=Path(h['begin']['ownedTempRoot']);assert not temp.is_symlink() and not list(temp.iterdir()) and not list(Path(h['begin']['testCwd']).iterdir());assert dict(device=temp.stat().st_dev,inode=temp.stat().st_ino,mode=temp.stat().st_mode & 0o777)==h['begin']['ownedTempRootIdentity']
 docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2366_ScenarioWriter所有fixture五是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2367_ScenarioWriter所有fixture五是正_製造単体結果.md','evidence/01_PT/018_NK-OPS-001/2368_ScenarioWriter元owner追補訂正.md']}
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=8,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,failedToolManifestHashes=failures,relatedBugs=['BUG1992','BUG1993','BUG1994'],relatedYkt=['YKT1740','YKT1741','YKT1742'],horizontalExpansionComplete=False,pendingExpansion=['YKT1739 ReadyFileInspector native closed candidate HOLD'],implementationDecision='PG-D753',canonicalWriterOwner='WBS-P008-06',canonicalVerifierOwner='WBS-P008-03',allMainClassesUnchanged=1843,changedTestPhysical=2,allOtherTestPhysicalUnchanged=1960,selectedWriterVerifierCounters=totals,directWriterVerifierClasses=p['directWriterVerifierClasses'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],ownedTempRootEmptyAfter=True,ownedTempIdentityUnchanged=True,actualOwnedSyntheticFileIoOnly=True,manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=2,staticActualExit=1,sourceRawCorrections=5,sourceDerivedRaw=8493,totalCorrections=924,oldContextRebindings=2,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=2,productTestFailures=0,implicitNoSuchAlgorithmFailureInjected=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
