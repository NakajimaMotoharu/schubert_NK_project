"""Check the Protocol JDBC fence on the preserved exact four-artifact graph."""

from datetime import datetime, timezone
from pathlib import Path
import runpy

STORAGE = runpy.run_path(str(Path(__file__).with_name("5330_f02_storage_jdbc_saved_edges.py")))
BASE = STORAGE["BASE"]
GRAPH = STORAGE["GRAPH"]


def main():
    read, ref, verified, write = (BASE[name] for name in ("read", "ref", "verified", "write"))
    start = read(next(BASE["H"].glob("706_F02*.json")))
    scope = start["values"]
    core, source, design = (scope[key] for key in ("productionCoreMain", "source", "canonicalDesignSource"))
    git = GRAPH["git"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    assert git("rev-parse", "origin/main").decode().strip() == design
    assert not git("diff", "--name-only", core, source, "--", "src", ":(exclude)src/**/src/test/**")
    checkpoint, http, package, graph, historical = map(verified, scope["oracleReferences"])
    assert checkpoint["storageRule"] == "NOT_SATISFIED"
    assert core == checkpoint["productionCoreMain"] == package["sourceCore"] == graph["source"]
    assert http["productionCore"] == core and historical["source"] != core
    assert package["actualExit"] == graph["actualExit"] == 0
    build_ref = package["reusableEvidence"][0]
    build = verified(build_ref)
    assert build["sourceCore"] == core and build["actualExit"] == 0 and build["inputHashesReverified"]
    assert package["reusableEvidence"][1] == scope["oracleReferences"][3]
    hashes = build["physicalClassHashes"]
    protocol = package["jars"]["protocol"]
    identity = STORAGE["owned_jar"](protocol["artifact"], hashes["protocol"])
    assert identity["classEntries"] == protocol["classes"] == 176
    rows, owners = STORAGE["reconstruct"](graph, hashes)
    scoped = [row for row in rows if owners[row[0]] == "protocol"]
    assert len(scoped) == http["outboundEdges"]["protocol"] == 2609
    assert {origin for origin, _, _ in scoped} == {name for name in owners if owners[name] == "protocol"}
    namespaces = STORAGE["JDBC_NAMESPACES"]
    matches = sorted(dict(origin=a, target=b, artifact=c) for a, b, c in scoped
                     if c == "java.sql" or b.startswith(namespaces))
    assert not matches
    design_path = next(Path("documents/300_SS").glob("310*/311_*.md"))
    b = git("show", f"{design}:{design_path}")
    assert "JDBC" in next(line for line in b.decode().splitlines()
                          if line.startswith("| `schubert-nk-protocol`"))
    report = dict(actualExit=0, source=source, productionCore=core, startEventId=start["eventId"],
                  criterionResult="PROTOCOL_JDBC_CLEAR_IN_SAVED_TYPED_EDGES",
                  scope="Protocol only. Storage BUG-3233 and cross-module end conditions remain open.",
                  originalEvidence=scope["oracleReferences"], physicalBuild=build_ref,
                  typedEdgeArchive=graph["checked"],
                  design=dict(path=str(design_path), sha256=GRAPH["sha"](b), source=design,
                              section="2 product module table, Protocol JDBC prohibition"),
                  protocolJar=identity, protocolTypedEdgeDenominator=len(scoped), violations=matches,
                  jdbcClassNamespaces=namespaces, matchedJdkArtifact="java.sql",
                  observedAggregate=graph["currentTypedEdges"], historicalReplays=0, newProductTests=0,
                  newJdepsRuns=0, newBuilds=0, newFormalAcceptance=0,
                  verifier=ref(Path(__file__)), sharedVerifier=ref(Path(STORAGE["__file__"])),
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = BASE["E"] / scope["run"]
    folder.mkdir()
    out = folder / "manifest.json"
    write(out, report)
    print(ref(out), identity["classEntries"], len(scoped), len(matches))


if __name__ == "__main__":
    main()
