"""Match the named monitoring mode candidates to retained public raw measurements."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


def pin(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def report_source(report):
    return next((report[key] for key in ("productionCoreMain", "currentCore", "source")
                 if isinstance(report.get(key), str) and len(report[key]) == 40), None)


def class_measurements(report_path, candidates, source, paths):
    located = []
    for line in report_path.read_text().splitlines():
        row = line.split("\t")
        if len(row) >= 7 and row[0] == "CLASS" and row[1] in candidates:
            located.append(row)
    if not located:
        return []
    receipt = report_path.with_name("manifest.json")
    if not receipt.is_file():
        return []
    proof = json.loads(receipt.read_bytes())
    older = report_source(proof)
    if older is None or type(proof.get("actualExit")) is not int or proof["actualExit"] != 0:
        return []
    result = []
    for row in located:
        name, crc64, matched = row[1:4]
        if matched != "true":
            continue
        path = paths[name]
        changed = subprocess.run(["git", "diff", "--quiet", older, source, "--", path],
                                 check=False, capture_output=True, timeout=30)
        if changed.returncode != 0:
            continue
        counters = {kind: dict(missed=int(missed), covered=int(covered))
                    for kind, missed, covered in (item.split(":") for item in row[6:])}
        assert len(counters) == 6
        result.append((name, dict(source=older, raw=pin(report_path), original=pin(receipt),
                                  crc64=crc64, counters=counters)))
    return result


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1446_*.json"))
    g = json.loads(plan.read_bytes())
    v = g["values"]
    assert all(pin(Path(row["path"])) == row for row in v["oracleReferences"])
    input_file = Path(v["oracleReferences"][1]["path"])
    rows = json.loads(input_file.read_bytes())
    source = v["productionCoreMain"]
    assert rows["source"] == source and len(rows["sourceCandidates"]) == 23
    paths = {p.split("/src/main/java/")[1].removesuffix(".java"): p for p in rows["sourceCandidates"]}
    assert len(paths) == 23
    root = input_file.parent.parent
    matches = {name: [] for name in paths}
    tables = sorted(root.glob("PG*/unfiltered.tsv"))
    for table in tables:
        for name, proof in class_measurements(table, matches, source, paths):
            matches[name].append(proof)

    result = []
    for name, path in paths.items():
        history = matches[name]
        passed = [entry for entry in history if all(x["missed"] == 0 for x in entry["counters"].values())]
        if passed:
            status = "SAME_JAVA_SOURCE_FULL_CLASS_COUNTERS_IN_RETAINED_RUN"
        elif history and any(entry["counters"]["BRANCH"]["missed"] == 0 for entry in history):
            status = "SAME_JAVA_SOURCE_BRANCH_ONLY_OR_PARTIAL"
        elif history:
            status = "SAME_JAVA_SOURCE_ONLY_PARTIAL_RAW"
        else:
            status = "NO_MATCHED_CURRENT_CLASS_IN_SCOPED_RAW_TABLES"
        blob = subprocess.check_output(["git", "rev-parse", f"{source}:{path}"], text=True).strip()
        result.append(dict(path=path, gitBlob=blob, className=name, status=status,
                           best=passed[-1] if passed else (history[-1] if history else None),
                           historicalMatches=len(history)))
    count = Counter(row["status"] for row in result)
    out = root / v["run"]
    out.mkdir()
    record = dict(actualExit=0, startEvent=g["eventId"], source=source, scope=v["run"],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), candidates=pin(input_file),
                  publicNamedTableCount=len(tables), counterResults=count, sites=result,
                  productTestsExecuted=0, analyzerExecutions=0, physicalOldExecCombined=0,
                  yktClosed=False, wholeF03=False, whole451=False, formalDelta=0)
    (out / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(count)
    print([(Path(row["path"]).stem, row["status"]) for row in result])


if __name__ == "__main__":
    main()
