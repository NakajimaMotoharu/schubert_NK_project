"""Register the ten current eligible public filenames with explicit existing owners."""

import json
from datetime import datetime, timezone
from pathlib import Path
import re
import runpy
import subprocess


BASE = runpy.run_path(str(Path(__file__).with_name("5437_g1307_jdbc_registry_binding.py")))
ROOT, PMO, PLAN, OPS, BIND = (BASE[k] for k in ("ROOT", "PMO", "PLAN", "OPS", "BIND"))
sha, proof, git, paths = (BASE[k] for k in ("sha", "proof", "git", "paths"))
eligible_names, value_digest = (BASE[k] for k in ("eligible_names", "value_digest"))
member = BASE["serialized_member"]
CHAR = "program/characterization/src/main/java/dev/codex/schubert/characterization/"
MON = "src/deployment/monitoring/"
SPECS = {
    **{CHAR + name: ("WBS-P020-01", "JAVA", basis) for name, basis in (
        ("CharacterizationIoScope.java", "SS355/PG-D-1171、比較機構内のIO所有"),
        ("CorrelatedLogEvidenceValidator.java", "SS355 §8.1、L01の公開比較入力"),
    )},
    **{MON + name: ("WBS-C07", "CONFIG", "SS351、監視配備テンプレート・手順") for name in (
        "grafana/README.md", "grafana/datasources-debug.yml.template",
        "grafana/datasources-standard.yml.template", "grafana/grafana.ini.template",
        "prometheus/README.md", "prometheus/debug-arguments.json.template",
        "prometheus/debug.yml.template", "prometheus/standard.yml.template",
    )},
}


def main():
    start = json.loads(next(PLAN.glob("1147_G1307*")).read_bytes())
    task = start["values"]
    assert all(proof(ROOT / ref["path"]) == ref for ref in task["oracleReferences"])
    core = task["productionCoreMain"]
    current = set(eligible_names(paths(core)))
    inv, snap = (next(PMO.glob(pattern)) for pattern in ("485_*", "486_*"))
    old_inv, old_snap = inv.read_bytes(), snap.read_bytes()
    inventoried, status = json.loads(old_inv), json.loads(old_snap)
    assert status["inventorySha256"] == sha(old_inv)
    previous = inventoried[BIND]
    path = ROOT / previous["path"]
    assert proof(path) == previous
    binding = json.loads(path.read_bytes())
    previous_rows = inventoried["artifacts"]
    already = {x["path"] for x in previous_rows}
    assert len(previous_rows) == len(already) == 1124
    assert current - already == set(SPECS)
    assert already - current == set(binding["retainedRetiredHistoricalPaths"])
    tasks = {a["id"]: a for a in json.loads(next(PMO.glob("481_*")).read_bytes())["tasks"]}
    added = []
    for name, (owner, kind, basis) in sorted(SPECS.items()):
        assert tasks[owner]["executionRole"] != "REFERENCE_ONLY"
        raw = git("show", f"{core}:{name}")
        assert (ROOT / name).read_bytes() == raw
        row = {
            "path": name, "kind": kind, "owner": owner, "costOwner": owner,
            "basis": basis, "sha256": sha(raw), "acceptance": "UNASSESSED",
        }
        if kind == "JAVA":
            row["module"] = "characterization"
            row["class"] = name.split("/src/main/java/", maxsplit=1)[1][:-5].replace("/", ".")
        added.append(row)
    assert len(added) == 10
    rows = added + previous_rows
    observed = git("rev-parse", "HEAD").decode().strip()
    new_binding = {
        **binding, "observedGitHead": observed, "productionCoreMainAtObservation": core,
        "registrySemanticSha256": value_digest(rows),
        "registeredAdditions": sorted([*binding["registeredAdditions"], *SPECS]),
        "predecessorBinding": previous,
    }
    out = OPS / task["run"]
    out.mkdir(exist_ok=True)
    certified = out / "preparation-registry-binding.json"
    frozen = json.dumps(new_binding, ensure_ascii=False, indent=2).encode() + b"\n"
    if certified.exists():
        assert certified.read_bytes() == frozen
    else:
        certified.write_bytes(frozen)
    frozen_ref = proof(certified)
    pointer = member(BIND, previous)
    marker = rb'^  "artifacts": \[\n'
    assert old_inv.count(pointer) == 1
    inner = "\n".join("  " + line for line in
                      json.dumps(added, ensure_ascii=False, indent=2).splitlines()[1:-1]).encode()
    new = old_inv.replace(pointer, member(BIND, frozen_ref))
    new, matched = re.subn(marker, lambda m: m[0] + inner + b",\n", new, flags=re.M)
    assert matched == 1
    assert json.loads(new) == {**inventoried, BIND: frozen_ref, "artifacts": rows}
    inv_digest = sha(new)
    updated, occurrences = re.subn(rb'("inventorySha256": ")[0-9a-f]{64}(")',
                                   lambda m: m[1] + inv_digest.encode() + m[2], old_snap)
    assert occurrences == 1 and json.loads(updated) == {**status, "inventorySha256": inv_digest}
    inv.write_bytes(new)
    snap.write_bytes(updated)
    cmd = ["python3", "-B", str(ROOT / "tools/quality/wbs_progress_audit.py"),
           "--current-source-structure-only"]
    verified = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=35)
    if verified.returncode:
        print(verified.stderr.decode().splitlines()[-1])
        return verified.returncode
    structure = json.loads(verified.stdout)
    assert structure["laterPreparationRegistry"]["preparationRows"] == 1134
    assert len(current) == len(rows) - 2 == 1132
    assert current == {row["path"] for row in rows} - set(binding["retainedRetiredHistoricalPaths"])
    result = dict(
        actualExit=0, source=observed, productionCore=core, startEvent=start["eventId"],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), registered=added, inputRefs=task["oracleReferences"],
        previousRegistryRowsPreserved=1124, previousBinding=previous, currentBinding=frozen_ref,
        inventory=proof(inv), snapshot=proof(snap), command=cmd, structure=structure, runner=proof(Path(__file__).resolve()),
        oldCurrentPathMissing=10, newCurrentPathMissing=0, activeCurrentPaths=len(current),
        retiredHistoricalPathCount=2, nativeOrActualServiceActions=0, actualProductTests=0,
        wholeG13=False, whole451=False, formalDelta=0, completedOriginalRowPricePp=0,
    )
    report = out / "manifest.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(proof(report), len(current), len(added))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
