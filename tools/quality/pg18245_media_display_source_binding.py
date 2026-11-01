"""Bind existing same-source media proofs without product replay or actual file acceptance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18245-media-display-source-binding-v1'
RECORDS=[["PG18229-media-display-review-v1","e1e51b97d1e27e258c5a5d987f67149b434dbf96caa430ddc177801260b28674"],["PG18230-media-display-twelve-pt-v1","849dd6e2f213158bda3df193489f75b604b27328ed12f437de6bd05f83e9f140"],["PG18232-media-display-twelve-post-v1","e492146f19bfaeb173f9680f96d041fa2e6ad7df57659f29f6b70aa50ab49832"],["PG18234-media-display-twelve-independent-v1","628dea9c861c897d6e50a3c0afdff2fe4756b814832a55b588704fb7960320cc"],["PG18238-current2937-media-display-registry-v1","0a8a2f43c4eed352e40b73003297244475c34bafe48df79f1899b7c818ee0358"],["PG18240-current2937-media-display-registry-post-v1","0377c0c250b52fbcb55743315f94fd1bfaf2474d1e21265760e553e12cbf26d0"],["PG18242-current2937-media-display-wbs-v1","9b6837eedaa593969516f1cb6124c528eeed4894c9ea1e61a56a2075fa465a3d"],["PG18244-current2937-media-display-wbs-post-v1","8f5cbfd1277a720b58b6003c349921e4290b59819b44ae01265dfd18b486d832"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2937,440,229,3092,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(2,631,1072,328,480,200,218)
    p=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    assert p['stubDescriptorContentHashNotVerified'] is True and p['actualFileContentOrHashValidated'] is False and len(p['officialFilteredSyntheticClasses'])==1
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=2,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=12,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualFileContentOrHashValidated=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
