"""Reconcile present class references with physical ownership in the four admitted JARs."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
JDEPS = ROOT.parent / "toolchain/jdk-25.0.4/bin/jdeps"
EXPECTED = {
    "protocol": set(),
    "storage": set(),
    "bootstrap": {"storage"},
    "batch": {"bootstrap", "storage"},
}
DENIED = {"TemporaryInfrastructureException", "FingerprintKeyRing",
          "ResponseSnapshotCodec", "WebStartupException"}
LEGACY = ("dev.codex.schubert.nk.storage.StorageIoException", "java.sql.SQLException")
ROW = re.compile(r"^\s+(\S+)\s+->\s+(\S+)\s+(.+?)\s*$")


def proof(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def run(*args):
    return subprocess.run(
        list(map(str, args)), cwd=ROOT, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        capture_output=True, timeout=60,
    )


def pom_edges(raw):
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    edges = set()
    for node in ET.fromstring(raw).findall("m:dependencies/m:dependency", ns):
        name = node.findtext("m:artifactId", namespaces=ns)
        scope = node.findtext("m:scope", default="compile", namespaces=ns)
        if name.startswith("schubert-nk-") and scope in ("compile", "runtime"):
            edges.add(name.removeprefix("schubert-nk-"))
    return edges


def main():
    start = json.loads(next(PLAN.glob("1108_F02現四*")).read_bytes())
    task = start["values"]
    refs = task["oracleReferences"]
    assert all(proof(Path(ref["path"])) == ref for ref in refs)
    package = json.loads(Path(refs[1]["path"]).read_bytes())
    history = json.loads(Path(refs[2]["path"]).read_bytes())
    core = task["productionCoreMain"]
    assert package["candidateProductionSource"] == core and package["actualExit"] == 0
    assert run("git", "rev-parse", "HEAD").stdout.decode().strip() == task["source"]
    assert run("git", "diff", "--exit-code", core, "--", "src", "pom.xml").returncode == 0
    assert tuple((item["origin"], item["target"])
                 for item in history["knownStorageNonVendorSqlEdges"]) == (LEGACY,)
    artifacts = package["privateJars"]
    assert set(artifacts) == set(EXPECTED)
    ownership = {}
    inputs = {}
    for module, receipt in artifacts.items():
        entry = receipt["artifact"]
        jar = Path(entry["path"])
        assert proof(jar) == entry
        path = f"src/schubert-nk-{module}/pom.xml"
        pom = run("git", "show", f"{core}:{path}")
        assert pom.returncode == 0 and pom_edges(pom.stdout) == EXPECTED[module]
        with ZipFile(jar) as archive:
            names = [n for n in archive.namelist() if n.endswith(".class")]
            assert len(names) == len(set(names)) == receipt["classes"]
            for name in names:
                assert Path(name).stem.split("$")[0] not in DENIED
                binary = name.removesuffix(".class").replace("/", ".")
                assert binary not in ownership
                ownership[binary] = module
        inputs[module] = {"jar": entry, "pomPath": path, "pomSha256": sha256(pom.stdout).hexdigest(),
                          "physicalClasses": len(names), "expected": sorted(EXPECTED[module])}
    assert len(ownership) == package["physical"] == 1102
    command = [str(JDEPS), "-verbose:class", "-filter:none", "--ignore-missing-deps",
               *(v["jar"]["path"] for v in inputs.values())]
    out = OPS / task["run"]
    out.mkdir()
    begun = datetime.now(timezone.utc).isoformat()
    proc = run(*command)
    stdout = out / "jdeps.stdout.gz"
    stdout.write_bytes(gzip.compress(proc.stdout, mtime=0))
    stderr = out / "jdeps.stderr.gz"
    stderr.write_bytes(gzip.compress(proc.stderr, mtime=0))
    rows = [ROW.fullmatch(line) for line in proc.stdout.decode().splitlines()
            if line.startswith(" ") and " -> " in line]
    assert all(rows) and rows
    edges = Counter()
    per_module = Counter()
    relevant_library_edges = []
    unresolved = []
    unique = set()
    for row in rows:
        origin, target, location = row.groups()
        assert origin in ownership and (origin, target) not in unique
        unique.add((origin, target))
        source_module = ownership[origin]
        dest_module = ownership.get(target)
        per_module[source_module] += 1
        if dest_module and source_module != dest_module:
            edges[f"{source_module}->{dest_module}"] += 1
        if source_module in ("storage", "protocol") and (
            target.startswith(("java.sql.", "javax.sql.", "org.postgresql.", "java.net.http.",
                               "jakarta.jms.", "org.springframework.", "jakarta.servlet."))
        ):
            relevant_library_edges.append((origin, target))
        if location == "not found":
            unresolved.append((origin, target))
    allowed = {f"{module}->{dest}" for module, targets in EXPECTED.items() for dest in targets}
    unknown_internal = sorted(row for row in unresolved if row[1].startswith("dev.codex.schubert.nk."))
    expected_observed = set(edges)
    okay = (proc.returncode == 0 and expected_observed == allowed and not unknown_internal
            and sorted(relevant_library_edges) == [LEGACY])
    report = {
        "source": task["source"], "productionCore": core, "run": task["run"], "startEvent": start["eventId"],
        "actualExit": 0 if okay else 1, "jdepsExit": proc.returncode, "command": command,
        "tool": proof(JDEPS), "runner": proof(Path(__file__)), "inputReceipts": inputs,
        "references": refs, "startedAtUTC": begun, "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
        "allPhysicalClasses": len(ownership), "classRows": len(rows), "perModule": dict(per_module),
        "interProductPairs": dict(edges), "undeclaredDirections": sorted(expected_observed - allowed),
        "unobservedDeclaredDirections": sorted(allowed - expected_observed),
        "unresolvedProduct": unknown_internal, "externalNotOnClasspath": len(unresolved)-len(unknown_internal),
        "restrictedLibraryRows": sorted(relevant_library_edges), "knownStorageJdbcRemainsOpen": True,
        "raw": [proof(stdout), proof(stderr)], "otherProductJarsIncluded": [],
        "newProductTests": 0, "wholeF02": False, "whole451": False, "formalAcceptance": 0,
    }
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print({key: report[key] for key in ("actualExit", "jdepsExit", "allPhysicalClasses", "classRows",
                                      "interProductPairs", "externalNotOnClasspath",
                                      "restrictedLibraryRows", "unresolvedProduct")})
    return report["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
