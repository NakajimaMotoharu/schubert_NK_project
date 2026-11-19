"""Check the SS311 Storage JDBC rule against the existing JAR and saved graph."""

from datetime import datetime, timezone
import gzip
import io
import os
from pathlib import Path
import runpy
import stat
from zipfile import ZipFile

BASE = runpy.run_path(str(Path(__file__).with_name("5239_f02_jdbc_state_lock_delta.py")))
GRAPH = BASE["G"]
JDBC_NAMESPACES = ("java.sql.", "javax.sql.", "org.springframework.jdbc.", "org.postgresql.")


def owned_jar(artifact, expected_classes):
    file = Path(artifact["path"])
    assert file.resolve(strict=True) == file
    with os.fdopen(os.open(file, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
        before = os.fstat(stream.fileno())
        assert stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o664
        assert (before.st_uid, before.st_gid, before.st_nlink) == (1000, 1000, 1)
        payload = stream.read(2 * 1024 * 1024)
        after = os.fstat(stream.fileno())
    current = file.stat(follow_symlinks=False)
    stable_fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink",
                     "st_size", "st_mtime_ns", "st_ctime_ns")
    assert all(getattr(before, field) == getattr(after, field) == getattr(current, field)
               for field in stable_fields)
    assert len(payload) == before.st_size and GRAPH["sha"](payload) == artifact["sha256"]
    with ZipFile(io.BytesIO(payload)) as jar:
        assert jar.testzip() is None
        names = jar.namelist()
        assert len(names) == len(set(names))
        classes = {name: GRAPH["sha"](jar.read(name)) for name in names if name.endswith(".class")}
    assert classes == expected_classes
    return dict(artifact=artifact, size=before.st_size, ownerUid=before.st_uid, ownerGid=before.st_gid,
                mode="0664", links=before.st_nlink, classEntries=len(classes),
                matchedPhysicalClassHashes=len(classes), crcVerified=True)


def reconstruct(graph, physical_hashes):
    verified, ref = BASE["verified"], BASE["ref"]
    prior = verified(graph["reusableRefs"][0])
    original, _ = BASE["edge_history"](prior)
    command = verified(graph["checked"])
    assert command["actualExit"] == 0
    archive = Path(command["stdout"]["path"])
    assert ref(archive) == command["stdout"]
    data = gzip.decompress(archive.read_bytes())
    assert GRAPH["sha"](data) == command["originalStdoutSha256"]
    delta = GRAPH["edges"](data.decode())
    origins = {origin for origin, _, _ in delta}
    assert origins == {BASE["FULL"], BASE["FULL"] + "$StateAction"}
    rows = [row for row in original if row[0] not in origins] + delta
    owners = GRAPH["class_owners"](physical_hashes)
    assert len(rows) == len(set(rows))
    assert GRAPH["analyze"](rows, owners) == graph["currentTypedEdges"]
    return rows, owners


def main():
    read, ref, verified, write = (BASE[name] for name in ("read", "ref", "verified", "write"))
    start = read(next(BASE["H"].glob("703_F02*.json")))
    scope = start["values"]
    core, source, design = (scope[key] for key in ("productionCoreMain", "source", "canonicalDesignSource"))
    git = GRAPH["git"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    assert git("rev-parse", "origin/main").decode().strip() == design
    assert not git("diff", "--name-only", core, source, "--", "src", ":(exclude)src/**/src/test/**")
    checkpoint, http, jars, graph = map(verified, scope["oracleReferences"])
    assert core == checkpoint["productionCoreMain"] == http["productionCore"] == jars["sourceCore"] == graph["source"]
    assert "Storage JDBC rule" in http["remaining"]
    assert graph["storageSqlBlockOpen"] is True and jars["actualExit"] == graph["actualExit"] == 0
    build_ref = jars["reusableEvidence"][0]
    build = verified(build_ref)
    assert build["sourceCore"] == core and build["actualExit"] == 0 and build["inputHashesReverified"]
    assert jars["reusableEvidence"][1] == scope["oracleReferences"][3]
    storage = jars["jars"]["storage"]
    hashes = build["physicalClassHashes"]
    identity = owned_jar(storage["artifact"], hashes["storage"])
    assert identity["classEntries"] == storage["classes"] == 79
    rows, owners = reconstruct(graph, hashes)
    scoped = [row for row in rows if owners[row[0]] == "storage"]
    assert len(owners) == jars["inputClassCount"] == 1102
    assert len(scoped) == http["outboundEdges"]["storage"] == 983
    assert {origin for origin, _, _ in scoped} == {name for name in owners if owners[name] == "storage"}
    matches = sorted(dict(origin=a, target=b, artifact=c) for a, b, c in scoped
                     if c == "java.sql" or b.startswith(JDBC_NAMESPACES))
    assert matches == [dict(origin="dev.codex.schubert.nk.storage.StorageIoException",
                            target="java.sql.SQLException", artifact="java.sql")]
    finding_class = matches[0]["origin"].replace(".", "/") + ".class"
    design_path = next(Path("documents/300_SS").glob("310*/311_*.md"))
    design_bytes = git("show", f"{design}:{design_path}")
    table = next(line for line in design_bytes.decode().splitlines()
                 if line.startswith("| `schubert-nk-storage`"))
    assert "Spring/JMS/JDBC" in table and b"native-only/no-JDBC" in design_bytes
    design_ref = dict(path=str(design_path), sha256=GRAPH["sha"](design_bytes), source=design,
                      section="2 product module table and SSC084/088")
    evidence = dict(actualExit=0, source=source, productionCore=core, startEventId=start["eventId"],
                    criterionResult="NOT_SATISFIED_ONE_FORBIDDEN_STORAGE_JDBC_EDGE",
                    originalEvidence=scope["oracleReferences"], physicalBuild=build_ref,
                    typedEdgeArchive=graph["checked"], canonicalDesign=design_ref, storageJar=identity,
                    fourModulePhysicalDenominator=len(owners), fourModuleTypedEdgeDenominator=len(rows),
                    storagePhysicalDenominator=identity["classEntries"], storageTypedEdgeDenominator=len(scoped),
                    jdbcClassNamespaces=JDBC_NAMESPACES, matchedJdkArtifact="java.sql",
                    violations=matches, violatingPhysicalClassSha256=hashes["storage"][finding_class],
                    existingBug="BUG-3233", relatedCrossCutting="YKT-2680",
                    uncovered=["Storage legacy entry and direct callback remediation under SSC461",
                               "Dependencies outside saved typed graph, including dynamic paths",
                               "API/Web artifacts, whole six-module build and runtime evidence", "451 and formal F02"],
                    newBuilds=0, newJdepsRuns=0, newProductTests=0, newFormalAcceptance=0,
                    verifier=ref(Path(__file__)), terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = BASE["E"] / scope["run"]
    folder.mkdir()
    report = folder / "manifest.json"
    write(report, evidence)
    print(ref(report), len(owners), len(rows), len(scoped), matches)


if __name__ == "__main__":
    main()
