"""Compare the fixture findings and the exact preserved Protocol class-edge inventory."""

from pathlib import Path
import runpy
import stat
from zipfile import ZipFile


RUN = runpy.run_path(str(Path(__file__).with_name("5351_f02_protocol_file_canaries.py")))
H, STORE, PLAN = (RUN[key] for key in ("H", "OPS", "PLAN"))
OLD = runpy.run_path(str(Path(__file__).with_name("5330_f02_storage_jdbc_saved_edges.py")))
FILE_OWNERS = {
    "java.nio.file.Files", "java.nio.file.FileSystems", "java.nio.file.FileSystem",
    "java.nio.file.FileStore", "java.nio.file.spi.FileSystemProvider",
    "java.io.File", "java.io.FileInputStream", "java.io.FileOutputStream", "java.io.FileReader",
    "java.io.FileWriter", "java.io.RandomAccessFile", "java.nio.channels.FileChannel",
    "java.nio.channels.AsynchronousFileChannel",
}


def main():
    read, verified = (OLD["BASE"][key] for key in ("read", "verified"))
    before, after = [next(STORE.glob(f"PG404{n}-*/manifest.json")) for n in (14, 16)]
    start = read(next(PLAN.glob("842_*")))
    values = start["values"]
    previous, present, independent = map(verified, values["oracleReferences"][3:])
    assert previous["sourceCore"] == present["productionCore"] == values["productionCoreMain"]
    assert independent["actualExit"] == 0 and present["actualExit"] == 0
    b, a = map(read, (before, after))
    assert a["productionCore"] == b["productionCore"] == previous["sourceCore"]
    assert a["inputPhysical"] == b["inputPhysical"] and len(a["caseChecks"]) == len(b["caseChecks"]) == 8
    assert b["correct"] == 4 and a["correct"] == 8 and b["stages"]["audit"]["actualExit"] == 0
    assert a["stages"]["audit"]["actualExit"] == 1
    assert not any(r["observed"] for r in b["caseChecks"])
    assert [r["target"] for r in a["caseChecks"] if r["observed"]] == [
        "java.nio.file.Files", "java.io.FileInputStream", "java.nio.channels.FileChannel",
        "java.nio.file.spi.FileSystemProvider"]
    assert not H["git"]("diff", "--name-only", b["source"], a["source"], "--", "src")
    for result in (b, a):
        assert all(H["pin"](Path(row[k]["path"])) == row[k]
                   for row in result["stages"].values() for k in ("stdout", "stderr"))

    history_path = next(STORE.glob("PG40254-*/manifest.json"))
    history = read(history_path)
    saved = verified(history["physicalBuild"])["physicalClassHashes"]
    graph = verified(history["originalEvidence"][3])
    jar = previous["jars"]["protocol"]["artifact"]
    identity = Path(jar["path"])
    assert identity.resolve() == identity and H["pin"](identity) == jar
    st = identity.lstat()
    assert stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o600
    assert present["qualifiedLocalArtifacts"]["protocol"]["artifact"] == jar
    with ZipFile(identity) as archive:
        assert archive.testzip() is None
        actual = {name: H["sha"](archive.read(name)) for name in archive.namelist() if name.endswith(".class")}
    assert identity.lstat() == st and actual == saved["protocol"]
    rows, owners = OLD["reconstruct"](graph, saved)
    protocol_edges = [(origin, target) for origin, target, _ in rows if owners[origin] == "protocol"]
    assert len(actual) == len({origin for origin, _ in protocol_edges}) == 176
    assert len(protocol_edges) == history["protocolTypedEdgeDenominator"] == 2609
    observations = [(origin, target) for origin, target in protocol_edges if target in FILE_OWNERS]
    assert not observations
    out = STORE / "PG40418-f02-protocol-file-independent-v1"
    out.mkdir()
    report = dict(actualExit=0, source=a["source"], productionCore=a["productionCore"],
                  originalStaticFixture=8, fixedForbidden=4, allowedUntouched=4,
                  oneCurrentProtocolJar=jar, exactCurrentPhysicals=176, archivedOutgoingTypedEdges=2609,
                  fileSpecificTypeEdges=observations, newProductJarsAnalyzedAtRuntime=0,
                  oldExecutionsReplayed=0, newJdepsRuns=0, productTests=0, formalDelta=0,
                  wholeF02Accepted=False, whole451Accepted=False, sourceEvidence=list(map(
                      H["pin"], (before, after, history_path))), terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", report)
    print(H["pin"](out / "manifest.json"))


if __name__ == "__main__":
    main()
