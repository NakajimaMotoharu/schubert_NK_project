"""Bind pure record serialization, not actual retirement, and separate necessary repeated tests."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17985-pure-retirement-source-binding-v1'
RECORDS=[["PG17969-pure-retirement-codec-review-v1","83188cd104366380404a18e8c47d026a53c3e208cd10032ea2484dbfee596ba5"],["PG17970-pure-retirement-codec-twelve-pt-v1","5bb7b7fdc77ba7fe89b06112999f8ae06649a2f27955ace7aaf8af918a1f9dfe"],["PG17972-pure-retirement-codec-twelve-post-v1","651a946af4db1a730567d32c7bb1484b002a33d72ffcea2410940820547124a2"],["PG17974-pure-retirement-codec-twelve-independent-v1","e6e9c17e02628aa6a860d78e95473d06c7cd49fd25b0c08520d02ae8ddadc96c"],["PG17978-current2850-pure-retirement-joint-registry-v1","a26ab8e71f29f594a80d960d6ad4ce72e5362ef798ee6526aed3fe78e6dbd7a2"],["PG17980-current2850-pure-retirement-joint-registry-post-v1","b32de2e4feea485b008d4768fa052ee724c52bb276ccae7df9f4df71ca18a423"],["PG17982-current2850-pure-retirement-joint-wbs-v1","7cd5783c6c959b5639b79ea34ab7d6fe13b1d47f1673b5581459c276fdcfb2e2"],["PG17984-current2850-pure-retirement-joint-wbs-post-v1","cb3697efe4787af8019873b657ccb0ff006da7b0383322ac99882ca161b7235b"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    old='dev/codex/schubert/nk/batch/file/MaintenanceRecords';new='dev/codex/schubert/nk/batch/repository/MaintenanceRetirement'
    assert m['fullSourceUnits'][old]['four100'] is m['fullSourceUnits'][new]['four100'] is True and m['jointQualificationReplacedUnitHistory'][old]['four100'] is False
    assert m['tests']==2850 and m['totalMethodExecutions']==2997 and m['totalRepeatedOriginalMethods']==147 and m['necessaryJointRepeatedMethods']==63 and len(m['jointQualificationReferences'])==6
    assert m['sourceProgramDelta']==1 and m['measuredSourcePrograms']==588 and m['four100SourcePrograms']==298
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,oldPartialProofPreserved=True,newMeasuredExistingProductionSources=1,newProductionFiles=0,newFour100Sources=2,newQualityCases=4,necessaryOriginalRepeatedCases=8,newOrdinaryCases=0,productTestsReexecutedByBinding=0,actualRetirementOrGcOperations=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
