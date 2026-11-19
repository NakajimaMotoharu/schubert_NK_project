"""Rebind the existing local summary proof and approved SQL contract to current inputs."""

from collections import Counter
from pathlib import Path
import re
import runpy


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[key] for key in ("EVIDENCE", "PLAN", "COMMON"))
DDL = "src/schubert-nk-api/src/main/resources/db/migration"
SS = "documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md"


def main():
    read = UPPER["read"]
    pin, git, sha = (COMMON[key] for key in ("pin", "git", "sha"))
    begin = read(next(PLAN.glob("827_*")))
    work = begin["values"]
    refs = work["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    prior, prepare, run, compiled, artifact, original = (read(meta["path"]) for meta in refs[1:7])
    assert prior["proofs"]["prepare"] == refs[2] and prior["proofs"]["unit"] == refs[3]
    assert run["actualExit"] == run["stages"]["unit"]["actualExit"] == prior["actualExit"] == 0
    assert run["tests"] == prior["tests"] == original["tests"] == 11
    assert not any(run[key] for key in ("failures", "errors", "skipped"))
    assert prior["notRun"] == 0 and not prior["oldExecUnion"] and not original["oldExecUnion"]

    core = work["productionCoreMain"]
    assert core == artifact["productionCore"] and core != prior["productionCoreMain"]
    assert not git("diff", "--name-only", core, work["source"], "--", "src")
    now = {name: value for module in compiled["classHashes"].values() for name, value in module.items()}
    source_pins = prepare["inputHashes"]
    assert len(source_pins) == 17
    assert all(sha(git("show", f"{work['source']}:{path}")) == old for path, old in source_pins.items())
    physical = prepare["physicalClassHashes"]
    assert len(physical) == prior["physicalClasses"] == 10
    assert all(now.get(path) == old for path, old in physical.items())
    assert set(prior["targetAndAdapterRaw"]) == {
        "dev/codex/schubert/nk/batch/repository/InspectionSummaryRepository",
        "dev/codex/schubert/nk/batch/repository/JdbcResourceFailures",
        "dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph",
    }
    assert all(not any(total["missed"] for total in counters.values())
               for counters in prior["targetAndAdapterRaw"].values())
    classes = Counter(case["classname"].rsplit(".", 1)[-1] for case in run["cases"])
    assert classes == {"InspectionSummaryPortTest": 10, "InspectionSummaryGraphContractTest": 1}
    names = set()
    for case in run["cases"]:
        identity = (case["classname"], case["name"])
        assert identity not in names and not any(case[field] for field in ("failure", "error", "skipped"))
        names.add(identity)

    design = work["canonicalDesignSource"]
    assert git("rev-parse", "origin/main").decode().strip() == design
    ss = git("show", f"{design}:{SS}")
    assert all(value in ss for value in (
        b"SSC049/PG162", b"SSC056/PG160", b"OffsetDateTime", b"queryTimeout5",
        b"READ COMMITTED", b"autoCommit=true", b"readOnly=false"))
    paths = git("ls-tree", "-r", "--name-only", core, "--", DDL).decode().splitlines()
    selected = {}
    for version in ("012", "016", "019"):
        name, = [path for path in paths if Path(path).name.startswith(f"V{version}__")]
        data = git("show", f"{core}:{name}")
        assert data == git("show", f"{prior['productionCoreMain']}:{name}")
        selected[version] = (name, data)
    summary = b"CREATE FUNCTION schubert.maintenance_read_inbox_summary("
    definition = rb"^CREATE(?: OR REPLACE)? FUNCTION schubert\.maintenance_read_inbox_summary\("
    assert sum(len(re.findall(definition, git("show", f"{core}:{path}"), re.M))
               for path in paths if path.endswith(".sql")) == 1
    assert all(part in selected["019"][1] for part in (
        summary, b"SET search_path = pg_catalog, schubert", b"SET timezone = 'UTC'",
        b"inspected_count bigint,deleted_count bigint,protected_count bigint,complete boolean",
        b"WHERE p.run_id=p_run_id", b"IF NOT FOUND THEN RETURN", b"progress.cutoff<>p_cutoff",
        b"pg_backend_pid()", b"mode='ExclusiveLock' AND granted",
        b"REVOKE ALL ON FUNCTION schubert.maintenance_read_inbox_summary(uuid,timestamptz) FROM PUBLIC;",
        b"GRANT EXECUTE ON FUNCTION schubert.maintenance_read_inbox_summary(uuid,timestamptz) TO schubert_batch;"))
    assert not re.search(rb"^[ \t]*(INSERT|DELETE|UPDATE)\b", selected["019"][1], re.I | re.M)
    assert b"PRIMARY KEY (run_id)" in selected["012"][1]
    assert b"schubert.maintenance_delete_inbox(" in selected["016"][1]
    assert b"p_expected_xact <> pg_catalog.pg_current_xact_id()::text" in selected["016"][1]

    result = dict(actualExit=0, source=work["source"], productionCore=core,
                  originUnitCore=prior["productionCoreMain"], originUnitSource=prior["source"],
                  samePhysicalByteEntries=sorted(physical), sameCompiledInputPaths=sorted(source_pins),
                  committedDdlSources=[dict(path=path, sha256=sha(data)) for path, data in selected.values()],
                  canonicalDesign=dict(source=design, path=SS, sha256=sha(ss)),
                  readOnlySummaryDefinitionCount=1, currentLocalJavaEvidenceCount=11,
                  oldSeparateP00402RunRetainedForHistory=11, historicalRunsCombined=False,
                  definitiveNativeOrDbPostconditions=0, productTestsExecuted=0, newProductCases=0,
                  preservedLocalPhysicalCounters=prior["targetAndAdapterRaw"],
                  cases=[dict(className=c, methodName=m) for c, m in sorted(names)],
                  sqlStaticContractObservations=[
                      "V012 durable progress run_id PK", "V016 reference-qualified deletion and same-transaction guard",
                      "V019 unique summary declaration, four typed columns, UTC, same active owner and run/cutoff",
                      "V019 current function grant/revoke source and no mutation statements"],
                  stillOpen=["Actual DB privilege, lock, row and committed postconditions",
                             "Held InboxCleanup with all required direct owners", "F02/F03/451"],
                  formalDelta=0, whole451Accepted=False, originalRowCompletionPricePp=0,
                  startEvent=begin["eventId"], sourceEvidence=refs[1:],
                  terminalAtUTC=COMMON["timestamp"]())
    output = STORE / work["run"]
    output.mkdir()
    COMMON["dump"](output / "manifest.json", result)
    print(pin(output / "manifest.json"))


if __name__ == "__main__":
    main()
