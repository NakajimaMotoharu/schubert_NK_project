"""Bind original whole8 and three static corrections, retaining raw6 and full-artifact gaps."""
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='915a8ed153b00d76a80164d36f9ce5b86d645046'
OUT=data.BASE/'PG12636-memory-boundary-completion-v1'
PINS={
 'host':('PG12620-memory-boundary-host-v1','42a5c55b0a4ea53bd1f579f62b12b6dbe614506cea6123c3da6e300ca54b8e98'),
 'post':('PG12624-memory-boundary-post-v1','38a996b54b2ccbff75e0697c340f97883080a0292e880e742707765f124d436c'),
 'context':('PG12626-memory-boundary-context-v1','28a41111573b2334cd70f720d5dfd8b311165180a3ce16854ad76b1b4d5a39f7'),
 'contextPost':('PG12628-memory-boundary-context-post-v1','8e70e55e3b30c4e608b26ab5b85e0e8a2476dd7a30b4d3ec94d563041a55266d'),
 'trace':('PG12630-memory-boundary-trace-v1','8a5d4b2f04a078dae812605ed4a27443cb0ce5b93c8d6396b7b4a954abe2f27c'),
 'tracePost':('PG12631-memory-boundary-trace-post-v1','7d9957a4a3f379ec24b9cb444212903fc2b248fbcd93efaf1a2b7a59687993ad'),
 'delta':('PG12632-current-memory-boundary-delta-v1','da59b0c8303e8b59d0f5601dd669185c0441dd6f6f6c8dcaba9589db1a12d06f'),
 'deltaPost':('PG12634-current-memory-boundary-delta-post-v1','5bd2474e044e8980f59678df3bd2a9da74504d24a7a5f3593c071f6626283f94')}

def main():
 invocation=capture(__file__);assert not OUT.exists()
 bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
 values={k:data.read_checked(data.BASE/name/'manifest.json',digest) for k,(name,digest) in PINS.items()}
 normal_sha='967ad00dfe1db5205d96530aac7da01d0b697ce9be29f61553c16db086c050e9'
 n=data.read_checked(data.BASE/'PG12618-memory-boundary-six-compile-v1/manifest.json',normal_sha)
 assert n['source']=='915a8ed15' and subprocess.check_output(['git','rev-parse',n['source']],cwd=data.ROOT,text=True).strip()==SOURCE
 assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items())
 h,p=values['host'],values['post'];assert h['actualExit']==p['actualExit']==0 and h['observedTestExecutions']==p['observedTestExecutions']==8
 assert h['begin']['normalSourceLiteral']==n['source'] and h['begin']['normalSourceResolved']==SOURCE and not h['oldExecUnion']
 assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==3 and p['otherTestPhysicalUnchanged']==1959 and p['forbiddenProbeHits']==0
 totals={kind:dict(missed=sum(v['counters'][kind]['missed'] for v in p['directMemoryClasses'].values()),covered=sum(v['counters'][kind]['covered'] for v in p['directMemoryClasses'].values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
 assert totals==dict(LINE=dict(missed=0,covered=64),METHOD=dict(missed=0,covered=14),CLASS=dict(missed=0,covered=2),BRANCH=dict(missed=0,covered=36))
 st=data.read_checked(data.BASE/'PG12622-memory-boundary-static-v1/manifest.json','d4cf88fc455039623e235190936553ad1d55c420c047fc5f693646f02f8e6011')
 assert st['source']==SOURCE and st['actualExit']==1 and st['reports']['pmd']['findings']==6 and st['reports']['checkstyle']['findings']==0
 assert values['context']['sourceContexts']==6 and values['contextPost']['metadataNegativeVectors']==22 and values['delta']['sourceDerivedRaw']==8504 and values['deltaPost']['totalPriorCorrections']==913
 assert values['tracePost']['oldRowsChangedShaOnly']==2 and values['tracePost']['wholeWbsAuditAfter']['actualExit']==1
 plan=data.read_checked(data.BASE/'PG12616-memory-boundary-plan-v1/manifest.json','82e5f9364cd979f4aebeef8bd3a8b2c72a3f720e432637383210c5d57c394c16')
 assert plan['metadataNegativeVectors']==11 and plan['conditionReferences']==3 and plan['allMainAndOtherInputsUnchanged']
 docs={p:data.sha((data.ROOT/p).read_bytes()) for p in ['evidence/01_PT/018_NK-OPS-001/2360_メモリ入力CSRF二Test三境界命名_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2361_メモリ入力CSRF二Test三境界命名_製造単体結果.md']}
 assert not list(Path(h['begin']['testCwd']).iterdir())
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,originalNormalManifestSha256=normal_sha,normalLiteralSource=n['source'],normalResolvedFullSource=SOURCE,normalOriginalManifestNotRewritten=True,actual=dict(tests=8,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG1988'],relatedYkt=['YKT1736'],implementationDecision='PG-D750',allMainClassesUnchanged=1843,changedTestPhysical=3,allOtherTestPhysicalUnchanged=1959,selectedMemoryTwoCounters=totals,measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=6,staticActualExit=1,sourceRawCorrections=3,sourceDerivedRaw=8504,totalCorrections=913,oldContextRebindings=6,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
