"""Prepare the four November 25 handoffs from pinned published terminal evidence."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


PLAN = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")


def load(path):
    return json.loads(Path(path).read_bytes())


def checked(ref):
    data = Path(ref["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == ref["sha256"]
    return data


def main():
    start = load(next(PLAN.glob("757_*")))
    work = start["values"]
    refs = work["oracleReferences"]
    prior, jar, protocol, timeout, env, storage_edges, protocol_edges = (
        json.loads(checked(ref)) for ref in refs[2:]
    )
    checked(refs[0])
    old_handoff = subprocess.check_output(
        ["git", "show", work["source"] + ":" + refs[1]["path"]], timeout=20)
    assert hashlib.sha256(old_handoff).hexdigest() == refs[1]["sha256"]
    core = work["productionCoreMain"]
    assert prior["source"] == jar["sourceCore"] == protocol["productionCoreMain"] == core
    assert timeout["productionCore"] == env["productionCore"] == core
    assert storage_edges["productionCore"] == protocol_edges["productionCore"] == core
    assert all(record["actualExit"] == 0 for record in
               (prior, jar, protocol, timeout, env, storage_edges, protocol_edges))
    historical = prior["historicalSsc447"]
    assert [historical[key] for key in ("success", "failed", "errors", "skipped", "notRun")] == [
        152, 0, 0, 0, 0]
    assert historical["appliedToCurrentSource"] is False
    for ref in historical["references"]:
        checked(ref)
    assert prior["externalHandoffReceipt"] is None
    package_counts = {name: item["classes"] for name, item in jar["jars"].items()}
    assert len(package_counts) == 4 and sum(package_counts.values()) == 1102
    assert len(storage_edges["violations"]) == 1 and protocol_edges["violations"] == []
    assert protocol["currentInputInventory"]["count"] == 169
    assert protocol["currentPhysical"]["count"] == 176 and not protocol["wholeF03Accepted"]
    directives = {(row["service"], row["directive"]): row for row in timeout["timeoutRows"]}
    assert [directives[(service, name)]["literal"] for service in ("api", "web")
            for name in ("TimeoutStartSec", "TimeoutStopSec")] == ["120s", "60s", "120s", "30s"]
    assert all(row["effectiveObserved"] is None for row in directives.values())
    real = env["directObservation"]
    assert real["sameBoot"] and real["earlierRunFinished"] and real["freeBytes"] >= real["thresholdBytes"]
    assert env["case"]["testId"] == "PT-CHR-PREFLIGHT-FS-001" and env["case"]["priceAppliedToF04"] == 0
    assert env["exitDependency"]["decision"] == "NOT_ACCEPTED"
    for key in ("proof", "independentPost", "frozen"):
        checked(env["case"][key])
    qualified = {
        "F02": dict(physicalByModule=package_counts, oldJdbcLegacyEdge=storage_edges["violations"],
                    protocolJdbcViolations=0, evidence=[refs[3], refs[7], refs[8]],
                    next="Same-source current API/Web two JARs, full approved dependency scope and 13 requirements."),
        "F03": dict(protocol=protocol["reusedStaticScope"], evidence=[refs[4]],
                    next="Complete authorized Batch applicability and actual six-module static quality with 451."),
        "C02": dict(templateTimeouts=timeout["timeoutRows"], evidence=[refs[5]],
                    next="Obtain the effective timeouts and same-invocation start/stop with the current owner and closure."),
        "F04": dict(fileStoreObservation=real, case=env["case"]["testId"], evidence=[refs[6]],
                    next="Qualify the next operation independently, then prove environment equivalence and 451."),
    }
    status = dict(actualExit=0, source=work["source"], productionCore=core, startEvent=start["eventId"],
                  deadlineJST=prior["deadlineJST"]["fourHandoff"], fourOwners=qualified,
                  ssc447Historical=historical, outsideRecipientReceipt=None,
                  formalAccepted=prior["officialAccepted"], formalTotal=prior["officialAll"],
                  formalPt=prior["officialPt"], formalScopes=prior["officialScope"], newFormalAcceptance=0,
                  newTests=0, newStaticRuns=0, priorTestsRanAgain=0, actualBackendActions=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), sourceReferences=refs)
    out = EVIDENCE / work["run"]
    out.mkdir()
    path = out / "manifest.json"
    with path.open("x") as stream:
        json.dump(status, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(path, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
