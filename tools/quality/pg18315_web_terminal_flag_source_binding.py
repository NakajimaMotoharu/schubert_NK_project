"""Bind pure captured flag proofs; no native terminal or process-owner acceptance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18315-web-terminal-flag-source-binding-v1'
RECORDS=[["PG18299-web-terminal-flag-review-v1","13e7884b5450f16b6249eb999268cddb74196218e4ec86bb93aa0a788d41a224"],["PG18300-web-terminal-flag-four-pt-v1","af06a7c2c8b234835b61c148d8bb3f0d9271b0f4b9e136bf081d1b370632c398"],["PG18302-web-terminal-flag-four-post-v1","df15b6c4de3afa0ddcddd150564a9b9ff860737950ecc907cbeda100b20d5777"],["PG18304-web-terminal-flag-four-independent-v1","5388221a81fe80ae03f3379bd197be6f8a7569e1b68ea4513ddba312da0d1682"],["PG18308-current2959-web-terminal-flag-registry-v1","a463cf67fb028fe17452fec23ee2ddbd8cb8a458c6533fa70bae7b0592dc4933"],["PG18310-current2959-web-terminal-flag-registry-post-v1","2ff8f372674c8d5eec2904da3f9acef8ed9f0fe5dd73241819cffd3d299c9770"],["PG18312-current2959-web-terminal-flag-wbs-v1","9ed3fbd86b6c035bfa765f6eb703aef99b8d2baec3bfbf9ec98de7f0c8fec187"],["PG18314-current2959-web-terminal-flag-wbs-post-v1","4a0f0edd2ac346fe06c4fa7a83759e711927c2123c77f9f2e617253d51f58f42"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2959,443,232,3114,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(1,642,1083,330,482,209,227)
    p=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    assert p['ownThreadCount']==p['actualOwnPlatformThreadCount']==4 and p['declaredOwnTaskCount']==64 and p['declaredOwnExecutorInstances']==1 and p['actualAllJvmThreadCount'] is None
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=1,newProductionFiles=0,newFour100Sources=0,newNaturalBranchZeroThreeCounterSources=1,newQualityCases=4,newOrdinaryCases=0,ownedWorkerCount=4,ownedTaskCount=64,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualNativeTerminalOrOwnedStopInvoked=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
