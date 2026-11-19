"""Apply the SS311 HTTP type check to sealed class-edge evidence without rebuilding jars."""

from collections import Counter
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import runpy

BASE = runpy.run_path(str(Path(__file__).with_name("5239_f02_jdbc_state_lock_delta.py")))
G = BASE["G"]
PREFIXES = ("java.net.http.", "com.sun.net.httpserver.")
LIBRARIES = ("protocol", "storage")


def main():
    read, ref, write, verified = (BASE[name] for name in ("read", "ref", "write", "verified"))
    start = read(next(BASE["H"].glob("669_F02*")))
    values = start["values"]
    core = values["productionCoreMain"]
    independent, jars, graph = map(verified, values["oracleReferences"])
    assert independent["afterMatched"] == 7 and independent["productJars"] == 0
    assert core == independent["productionCore"] == jars["sourceCore"] == graph["source"]
    assert not G["git"]("diff", "--name-only", core, values["source"], "--",
                        "src", ":(exclude)src/**/src/test/**")
    build_ref = jars["reusableEvidence"][0]
    build = verified(build_ref)
    assert build["sourceCore"] == core and build["inputHashesReverified"]
    assert jars["reusableEvidence"][1] == values["oracleReferences"][2]

    archived_prior = verified(graph["reusableRefs"][0])
    original, _ = BASE["edge_history"](archived_prior)
    receipt = verified(graph["checked"])
    packed = Path(receipt["stdout"]["path"])
    assert ref(packed) == receipt["stdout"]
    data = gzip.decompress(packed.read_bytes())
    assert G["sha"](data) == receipt["originalStdoutSha256"]
    assert receipt["actualExit"] == 0
    delta = G["edges"](data.decode())
    changed = {origin for origin, _, _ in delta}
    assert changed == {BASE["FULL"], BASE["FULL"] + "$StateAction"}
    rows = [row for row in original if row[0] not in changed] + delta
    owner = G["class_owners"](build["physicalClassHashes"])
    assert len(owner) == jars["inputClassCount"] == 1102
    assert len(rows) == len(set(rows))
    assert G["analyze"](rows, owner) == graph["currentTypedEdges"]

    observed = Counter()
    origins = set()
    violations = []
    for origin, target, artifact in rows:
        module = owner[origin]
        if module not in LIBRARIES:
            continue
        observed[module] += 1
        origins.add(origin)
        if target.startswith(PREFIXES):
            violations.append(dict(origin=origin, target=target, artifact=artifact))
    physical = Counter(owner[origin] for origin in origins)
    assert dict(physical) == {module: jars["jars"][module]["classes"] for module in LIBRARIES}

    folder = BASE["E"] / values["run"]
    folder.mkdir()
    proof = folder / "manifest.json"
    write(proof, dict(actualExit=0, source=values["source"], productionCore=core,
                       startEventId=start["eventId"], originalEvidence=values["oracleReferences"],
                       buildEvidence=build_ref, codeEvidence=graph["checked"], ownedPhysical=dict(physical),
                       outboundEdges=dict(observed), matchedPrefixes=PREFIXES, violations=violations,
                       criterionResult=("SATISFIED_FOR_SAVED_TWO_LIBRARY_CLASS_EDGES" if not violations
                                        else "VIOLATION_IN_SAVED_LIBRARY_CLASS_EDGES"),
                       newJdepsRuns=0, newProductBuilds=0, newProductTests=0, newFormalAcceptance=0,
                       remaining=["Same-source API/Web and all-six typed analysis", "Storage JDBC rule",
                                  "F02 runtime and 451 dependencies"],
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(ref(proof), dict(physical), dict(observed), len(violations))


if __name__ == "__main__":
    main()
