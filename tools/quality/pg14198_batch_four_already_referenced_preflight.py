"""Preflight only: all32 candidate catches already referenced, so no duplicate review or Product run."""
from pathlib import Path
import f03_main_failure_boundary_sixty_two_trace_v1 as trace
from host_tool_invocation import capture,verify

OUT=trace.data.BASE/"PG14198-batch-four-already-referenced-preflight-v1"
NAMES={"RunReferenceRepository","InspectionSummaryRepository","CleanupStepRepository","BackupStepRepository"}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    ids,refs,_=trace.state_after();catalog=trace.data.read_checked(trace.data.BASE/trace.ORIGINAL[0],trace.ORIGINAL[1])
    normal=trace.data.read_checked(trace.data.BASE/"PG13832-snapshot-program-six-compile-v1/manifest.json","8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65")
    assert normal["source"]==trace.SOURCE and normal["actualExit"]==normal["testsExecuted"]==0
    selected=[r for r in catalog if Path(r["path"]).stem in NAMES and r["rule"]=="AvoidCatchingGenericException"]
    assert len(selected)==len({r["id"] for r in selected})==32 and {Path(r["path"]).stem for r in selected}==NAMES
    assert all(r["id"] in ids and r["id"] in refs and r["inputSha256"]==normal["begin"]["inputHashes"][r["path"]] for r in selected)
    current={r["path"]:normal["begin"]["inputHashes"][r["path"]] for r in selected}
    assert all(trace.data.sha((trace.data.ROOT/p).read_bytes())==h for p,h in current.items())
    verify(invocation);OUT.mkdir()
    trace.data.write(OUT/"manifest.json",dict(actualExit=0,source=trace.SOURCE,invocation=invocation,originalCatalog=trace.ORIGINAL,referenceSetFunction="f03_main_failure_boundary_sixty_two_trace_v1.state_after",currentInputHashes=current,alreadyReferencedIds=[r["id"] for r in selected],alreadyReferenced=32,newSourceReferences=0,rawRetained=True,reclassificationPerformed=False,workClassification="REAUTHENTICATION_NOT_NEW_WORK_COMPLETION",indexBeforeBodyCorrectiveAction=True,bodyRereadLines=574,productTestsExecuted=0,coverage=None,sourceChanged=False,sourceDerivedRaw=6247,joinedReferences=3636,currentWholePending=2775,noReference=2611,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None,actualExternalOperations=0))
    print(trace.data.sha((OUT/"manifest.json").read_bytes()))
if __name__=="__main__":main()
