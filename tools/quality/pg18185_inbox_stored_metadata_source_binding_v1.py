"""Bind only public stored value tests, not cryptography or DB replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18185-inbox-stored-metadata-source-binding-v1'
RECORDS=[["PG18169-inbox-stored-metadata-review-v1","6fbc05f8492f24ac374d1b63bb24bee9afdd33208370d93f25301b4a91551e3d"],["PG18170-inbox-stored-metadata-six-pt-v1","8732089861b69d474eccd7c2e44f381efa269b4478bf428e1c78d65a55bd28e1"],["PG18172-inbox-stored-metadata-six-post-v1","f09918adbde8ed61e78c7af9fa6580bd66737dfed162fbb5a551b8bdb6b6d44e"],["PG18174-inbox-stored-metadata-six-independent-v1","bdcde187c1f5cc0649d87b43437dcdf51e6892218c257b29f5781a06ed0663f0"],["PG18178-current2907-inbox-stored-metadata-registry-v1","386637fbdac8b7eb7367b065c0fa6340f5c25ca9ce132ed37580885afc8d2778"],["PG18180-current2907-inbox-stored-metadata-registry-post-v1","2a0f7e69cdcba21c77696908ca5253547a11bd8b91ed637bda0afa98142fa857"],["PG18182-current2907-inbox-stored-metadata-wbs-v1","4a66481fa03e4679ecd867715d710086701e0b6a319062b112f87dfc82351525"],["PG18184-current2907-inbox-stored-metadata-wbs-post-v1","ade441e89efcc1a091b986d9722d4b96475c731122c1f08c3aa38e71cbb2823e"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2907,437,226,3062,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(4,623,1062,320,470,200,218)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=4,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=2,newQualityCases=6,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualCryptoOrReplayCertified=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
