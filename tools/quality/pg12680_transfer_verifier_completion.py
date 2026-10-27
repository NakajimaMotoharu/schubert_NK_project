"""Whole3 verifier fixture group closure, retaining writer/YKT and implicit exception gaps."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='8ccadeed207cf1f38264c35199bd4def12aae6c3'
OUT=data.BASE/'PG12680-transfer-verifier-completion-v1'
PINS={
 'normal':('PG12666-transfer-verifier-six-compile-v1','138b454a9eb9d3d00f6ac2579d6f76b36afbc340b745375d53dfa8383bf59e10'),
 'host':('PG12668-transfer-verifier-host-v1','1a49b9f669459d939feac578475608fe79836336328fe471fa8c2272bf383a4b'),
 'static':('PG12670-transfer-verifier-static-v1','9aadfc3732078e310172ff095fd03290e3544530e662db99ef341fbd98dddbe8'),
 'post':('PG12672-transfer-verifier-post-v1','5606c98f263fd7d0aeb157199382fad6b8513c51955c383f5bd7f20511483ad7'),
 'trace':('PG12674-transfer-verifier-trace-v1','ec60fdb82dc9c3ab811832d6b0e99342a88cdf39cec0a437c7c465ae55a24af6'),
 'tracePost':('PG12675-transfer-verifier-trace-post-v1','0925d73a86fa6fca5d33f08011989bcb89f18cf397244fdd689378d8d2a7a912'),
 'delta':('PG12676-current-transfer-verifier-delta-v1','d09c1ac0fe1e7d5b110376bf49a2d9ebe3086d757bf86822b3202798628f3d0e'),
 'deltaPost':('PG12678-current-transfer-verifier-delta-post-v1','266322bbe3f49af73a8d95713a0db0dd06c78661a4b1bfe5519125eefdc44795')}

def main():
 invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',h) for name,h in PINS.values()],SOURCE)
 v={k:data.read_checked(data.BASE/name/'manifest.json',h) for k,(name,h) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
 assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==3 and not h['oldExecUnion']
 assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
 assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==2 and p['otherTestPhysicalUnchanged']==1960 and p['forbiddenProbeHits']==0 and p['ownedTempRootEmptyAfter'] and p['ownedTempIdentityUnchanged']
 assert p['renamedInnerMapping']['before'].endswith('$TestInput.class') and p['renamedInnerMapping']['after'].endswith('$ChunkedInput.class')
 counters=p['directVerifierClasses']['dev/codex/schubert/nk/api/storage/TransferContentVerifier.class']['counters']
 assert counters==dict(LINE=dict(missed=0,covered=20),METHOD=dict(missed=0,covered=1),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=10))
 assert v['static']['reports']['pmd']['findings']==v['static']['reports']['checkstyle']['findings']==0 and v['static']['actualExit']==0
 assert v['delta']['sourceDerivedRaw']==8498 and v['deltaPost']['totalPriorCorrections']==919 and v['tracePost']['oldRowsChangedShaOnly']==1 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
 plan=data.read_checked(data.BASE/'PG12664-transfer-verifier-plan-v1/manifest.json','ea86a69bf4b7ca5d5aa70d7d1f825b6f80b1ee543eaeaca122dbb113c90bb155')
 assert plan['metadataNegativeVectors']==8 and plan['renamedIdentifierReferences']==8 and plan['finallyOwnerOnlyChange'] and plan['allMainAndOtherInputsUnchanged']
 temp=Path(h['begin']['ownedTempRoot']);assert not temp.is_symlink() and not list(temp.iterdir()) and not list(Path(h['begin']['testCwd']).iterdir())
 assert dict(device=temp.stat().st_dev,inode=temp.stat().st_ino,mode=temp.stat().st_mode & 0o777)==h['begin']['ownedTempRootIdentity']
 docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2364_TransferVerifier所有fixture三是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2365_TransferVerifier所有fixture三是正_製造単体結果.md']}
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=3,suites=1,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG1991'],relatedYkt=['YKT1739'],horizontalExpansionComplete=False,pendingExpansion=['ScenarioRecordStreamTest closed FileChannel same-cause closure not yet qualified'],implementationDecision='PG-D752',allMainClassesUnchanged=1843,changedTestPhysical=2,allOtherTestPhysicalUnchanged=1960,renamedInnerMapping=p['renamedInnerMapping'],selectedVerifierCounters=counters,directVerifierClasses=p['directVerifierClasses'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],ownedTempRootEmptyAfter=True,ownedTempIdentityUnchanged=True,actualOwnedSyntheticFileIoOnly=True,manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=0,staticActualExit=0,sourceRawCorrections=3,sourceDerivedRaw=8498,totalCorrections=919,oldContextRebindings=0,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,implicitNoSuchAlgorithmFailureInjected=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
