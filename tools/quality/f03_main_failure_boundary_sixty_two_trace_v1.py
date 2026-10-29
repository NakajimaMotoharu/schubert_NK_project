"""Join exactly62 reviewed Main generic catches; preserve all previous rows/runtime and pending status."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_main_monitor_eighty_one_trace_v2 import state_after as previous_state
from pg14188_owned_failure_boundaries_sixty_two_context import PLAN
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE="0061d178cda80c2ce3926290619c64db125dbcfc"
PRIOR=("PG14086-main-monitor-eighty-one-trace-v1","7ae5c6848478b409aa366c974e777aa25d0a7abac23fbe1b328e82d68d01580c")
REVIEW=("PG14188-owned-failure-boundaries-sixty-two-context-v1","f916ead8230d474c9b07b2d91c2952a6bccdd0dd696c4b292dc2b6a8ec5d59ce")
POST=("PG14190-owned-failure-boundaries-sixty-two-post-v1","f35b4257e4e2abb2f4cd997c144fd96422b9f0054ac39d1cd3f90759fa294a05")
OUT=data.BASE/"PG14192-main-failure-boundaries-sixty-two-trace-v1"
RECORD="evidence/01_PT/018_NK-OPS-001/2605_所有資源例外境界五Main六十二件_製造静的確認結果.md"
BASE="380d223f2447cd699a21803f990399bf0a3803a2"
ORIGINAL=("PG10690-current-global-static-post-v1/findings.json","92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966")
FIELD="currentMainFailureBoundarySixtyTwoReferences"
OVERLAY="mainFailureBoundariesPG14192Overlay"

def main_generic_ids():
    catalog=data.read_checked(data.BASE/ORIGINAL[0],ORIGINAL[1]);ids,_,_=previous_state()
    return {r["id"] for r in catalog if r["sourceKind"]=="MAIN" and r["rule"]=="AvoidCatchingGenericException"}&ids

def new_ids():
    ids,refs,pending=previous_state();remaining=main_generic_ids()-refs
    selected={i for v in PLAN["targets"].values() for i in v["ids"]}
    assert len(remaining)==520 and len(selected)==62 and selected<=remaining
    assert (len(ids),len(refs),len(pending))==(6247,3574,2713)
    return selected

def state_after():
    ids,refs,pending=previous_state();extra=new_ids()
    return ids,refs|extra,pending|extra

def inputs():
    prior=data.read_checked(data.BASE/PRIOR[0]/"manifest.json",PRIOR[1])
    review=data.read_checked(data.BASE/REVIEW[0]/"manifest.json",REVIEW[1]);post=data.read_checked(data.BASE/POST[0]/"manifest.json",POST[1])
    rows=data.read_checked(data.BASE/REVIEW[0]/"review.json",review["reviewSha256"])["rows"]
    assert review["source"]==post["source"]==prior["source"]==SOURCE and review["actualExit"]==post["actualExit"]==post["productTestsExecuted"]==0
    assert review["sourceContexts"]==post["sourceContexts"]==len(rows)==62 and review["sourceFiles"]==post["sourceFiles"]==5 and post["reviewManifestSha256"]==REVIEW[1]
    assert len({r["id"] for r in rows})==62 and {r["id"] for r in rows}==new_ids()
    assert all(r["rawRetained"] is r["currentWholeJoinPending"] is True and r["sourceChanged"] is False and type(r["productTestsExecuted"]) is int and r["productTestsExecuted"]==0 for r in rows)
    normal=data.read_checked(data.BASE/"PG13832-snapshot-program-six-compile-v1/manifest.json","8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65")
    assert normal["source"]==SOURCE and normal["actualExit"]==normal["testsExecuted"]==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal["begin"]["inputHashes"].items())
    assert len(prior["sourceRows"])==995 and all(r["sha256"]==normal["begin"]["inputHashes"][r["path"]] for r in prior["sourceRows"])
    raw,snap=[subprocess.check_output(["git","show",BASE+":"+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw)=="81e828f1fe3c9a79300e6ca4c4a2071a0e86b691883370892b43985c04d08773"
    assert data.sha(snap)=="553ef21fa96cb2a82bbdf425a402cd19828576e93b903daf8e2d4794afe11f82"
    return prior,sorted(rows,key=lambda r:r["id"]),raw,snap

def expected(prior,rows):
    ids,refs,pending=state_after();value=copy.deepcopy(prior)
    for k in ["invocation","wholeWbsAuditBefore"]:value.pop(k,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
      priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/"manifest.json").relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    value[FIELD]=dict(review=REVIEW,post=POST,source=SOURCE,rows=rows,newSourceReasonRows=62,newCurrentReferences=62,sourceFiles=5,rawRetained=62,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allAddedToGlobalJoinPending=True,currentMainGenericRaw=len(main_generic_ids()),previousUnreferencedMainGeneric=520,remainingUnreferencedMainGeneric=458)
    assert value["sourceRows"]==prior["sourceRows"] and value["currentQualification"]==prior["currentQualification"] and value["currentMainMonitorEightyOneReferences"]==prior["currentMainMonitorEightyOneReferences"]
    assert (len(refs),len(pending),len(ids-refs))==(3636,2775,2611)
    return value

def documents(value,raw,snap):
    original=json.loads(raw);result=raw
    overlay=dict(source=SOURCE,manifest=str((OUT/"manifest.json").relative_to(data.ROOT)),sha256=data.sha((OUT/"manifest.json").read_bytes()),record=RECORD,qualification=value[FIELD],joinedContextWarnings=3636,currentWholeJoinPending=2775,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=62,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section=copy.deepcopy(original[name]);assert OVERLAY not in section
        section[OVERLAY]=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    result_snap,_,_=replaced(snap,"inventorySha256",data.sha(result))
    validate_docs(result,result_snap,original,json.loads(snap))
    restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(OVERLAY)
    assert restored==original
    return result,result_snap
