"""Same-source Code-free population binding, failure preservation and joint-method units."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17865-codefree-source-binding-v1'
RECORDS=[["PG17842-codefree-main-diagnosis-v1","04763edb92a176b5c043b191af2266e281947590805c17cbf8d264e0c7b1b04d"],["PG17854-codefree-official-passive54-recovery-v3","6eb6c989f53530b4e6eb3d991c31561809aa0066b6600e08e5299713e9569cb7"],["PG17856-codefree-definitions-independent-v1","b19e91ce027660ce7b6aa8e1159b34e8280f469ca8b121f4268358ec746a8df6"],["PG17858-current2827-codefree17-registry-v1","1979776c9e85f43e9e69ed30ceb1dc7444c5bc5ad09b044f479eefff4c46d40f"],["PG17860-current2827-codefree17-registry-post-v1","cab0b503a6782a8cdf5f4bc88487be24f52a83449c693c8af3830b3a3a6ffd86"],["PG17862-current2827-codefree17-wbs-v1","b0d01c8755d30835da02ead836f654844cac896518596f10228298c002fb582d"],["PG17864-current2827-codefree17-wbs-post-v1","1a08f7f115e16f9afa231f5d584b527e825f7ea1eeca4c47ce790abe00450308"],["PG17816-admission-actual-wait-five-pt-v1","6eddd61a889e0ebb85a9f1eb3451ace5a272c803e1ee3b606cada04a21203f8e"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    p=data.read_checked(data.BASE/RECORDS[1][0]/'manifest.json',RECORDS[1][1]);registry=data.read_checked(data.BASE/RECORDS[3][0]/'manifest.json',RECORDS[3][1])
    assert p['interfaceZeroCounterSourceCount']==17 and p['officialPackageInfoDefinitionCount']==37 and p['passiveAnalyzerJvmCommandsIssuedByRecovery']==0
    assert registry['necessaryJointRepeatedMethods']==sum(v['necessaryRepeatedMethods'] for v in registry['jointQualificationReferences'])==51 and len(registry['jointQualificationReferences'])==4
    assert registry['totalMethodExecutions']==registry['tests']+registry['totalRepeatedOriginalMethods']==2962
    failures=[]
    for name,pin,slot,expected in [('pg17852_codefree_official_passive54_v1.py','6067173e37fe8ec88634b2972ae23e11ed846b3a08a087be0cfdb6639f16eed7','pg17852-codefree-official-passive54-v1',1),('pg17853_codefree_official_passive54_v2.py','3eac65d541c76ff57f1627aa291e43e02adf556adc02b47f7271b5a0ef4ccfbd','pg17853-codefree-official-passive54-v2',0)]:
        path=data.ROOT/'tools/quality'/name;assert data.sha(path.read_bytes())==pin
        exitpath=data.ROOT.parent/'pgpt-runs/PG379'/slot/'official-passive-zero-counters-exit.safe.json'
        stage=json.loads(exitpath.read_bytes());assert stage['actualExit']==expected and stage['timedOut'] is False
        failures.append(dict(entry=name,entrySha256=pin,originalBodyExit=1,originalAnalyzerExit=expected,exitPath=str(exitpath),exitSha256=data.sha(exitpath.read_bytes()),productTestsExecuted=0))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,failedProfilesPreserved=failures,officialClassModelScopes=17,separateNonRuntimePackageInfoDefinitions=37,newProductTests=0,newFour100=0,measurementPopulationCorrectionOnly=True,necessaryJointRepeatedMethods=51,jointQualificationRuns=4,totalRepeatedMethods=135,newAnalyzerJvmsIssued=0,sourceTransferred=False,coverageExecUnion=False,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
