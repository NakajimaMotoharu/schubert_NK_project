"""Bind fixed diagnostic bodies to the current Protocol JAR and existing independent cases."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile


ROOT = Path.cwd()
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
STEPS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
PROTOCOL = Path("src/schubert-nk-protocol")
TEST_ROOT = PROTOCOL / "src/test/java/dev/codex/schubert/nk/protocol/layout"
FIXTURES = PROTOCOL / "src/test/resources/protocol"
METHODS = {
    "allNamedTypesHaveIndependentDirectionalFieldMeaning",
    "explicitCatalogMatchesIndependentSs323NamedTypeFixture",
    "allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes",
}


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def receive(pattern):
    path, = OPS.glob(pattern + "*/manifest.json")
    return path, read(path)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def qualified_classes(path):
    base = "dev/codex/schubert/nk/protocol/"
    assert pin(path["path"]) == path
    with ZipFile(path["path"]) as jar:
        paths = [name for name in jar.namelist() if name.startswith(base) and name.endswith(".class")]
        assert len(paths) == len(set(paths)) == 176
        return {name: sha256(jar.read(name)).hexdigest() for name in paths}


def main():
    checkpoint, = STEPS.glob("3401_*")
    snapshot = read(checkpoint)
    active = snapshot["values"]
    core, source = active["productionCoreMain"], active["source"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    original, ordinary = receive("PG42624")
    current_path, packaged = receive("PG43046")
    assert ordinary["actualExit"] == packaged["actualExit"] == 0
    assert ordinary["normalCases"] == 171 and ordinary["suites"] == 39
    observed_tree = git("rev-parse", f"{core}:{PROTOCOL}").decode().strip()
    assert observed_tree == packaged["sameProtocolTree"]
    assert observed_tree == git("rev-parse", f"{ordinary['source']}:{PROTOCOL}").decode().strip()
    assert pin(original) in packaged["originalProofs"]
    live_jar = packaged["currentJar"]
    built = qualified_classes(live_jar)
    assert built == qualified_classes(ordinary["actualProductJar"])

    roster = ordinary["sanitizedCases"]
    assert pin(roster["path"]) == roster
    outcomes = [c for c in read(roster["path"])
                if c["className"].endswith(".PayloadTypeCatalogTest") and c["method"] in METHODS]
    assert len(outcomes) == 3 and all(c["outcome"] == "PASS" for c in outcomes)
    fixture_paths = [TEST_ROOT / name for name in ("PayloadTypeCatalogTest.java", "IndependentNamedFieldOracle.java")]
    fixture_paths.extend(FIXTURES / name for name in (
        "named-types-ss323.tsv", "named-accessors-independent.tsv", "fields-ui234-236.tsv", "layouts-ui233.tsv",
    ))
    for path in fixture_paths:
        assert path.read_bytes() == git("show", f"{core}:{path}")
    definitions = [line.split("\t") for line in (FIXTURES/"named-types-ss323.tsv").read_text().splitlines()
                   if line and not line.startswith("#")]
    assert len(definitions) == len({row[0] for row in definitions}) == 64
    assert sum(record != "-" for _, _, record in definitions) == 14
    identities = sorted({simple for _, data, record in definitions for simple in (data, record)
                         if simple != "-"})
    assert len(identities) == 69
    names = {}
    for simple in identities:
        path, = (name for name in built if name.endswith(f"/{simple}.class"))
        names[path.removesuffix(".class").replace("/", ".")] = built[path]

    javap = ROOT.parent / "toolchain/jdk-25.0.4/bin/javap"
    command = [str(javap), "-classpath", live_jar["path"], "-c", *sorted(names)]
    result = subprocess.run(command, capture_output=True, timeout=45, check=False)
    assert result.returncode == 0 and not result.stderr, result.returncode
    blocks = re.split(r"(?m)^Compiled from .+\n", result.stdout.decode("utf-8"))[1:]
    rows = {}
    for block in blocks:
        name = re.search(r"(?m)^public (?:final )?class (\S+)", block).group(1)
        simple = name.rsplit(".", 1)[1]
        found = re.search(
            r"(?m)^  public java\.lang\.String toString\(\);\n    Code:\n"
            r"\s*0: ldc(?:_w)? +#\d+ +// String (.+)\n"
            r"\s*[23]: areturn *\n(?=\n|\})", block,
        )
        assert found and found.group(1) == f"{simple}[REDACTED]", name
        rows[name] = dict(className=name, sha256=names[name], expectedDiagnostic=found.group(1))
    assert set(rows) == set(names) and len(blocks) == 69

    out = OPS / active["run"]
    out.mkdir()
    evidence = dict(run=active["run"], source=source, productCore=core, startEvent=snapshot["eventId"],
                    actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), wbs="WBS-P018-10.02/2",
                    design=["SS323", "SS351"], testId="PT-PRO-001-T01", original=pin(original),
                    qualifiedArchive=pin(current_path), archiveMain=live_jar, independentFixture=list(map(pin, fixture_paths)),
                    matchingProtocolReference=observed_tree, matchingPhysicalPopulation=len(built), requirements=dict(layouts=64, recordLayouts=14, fixedTypes=69),
                    originalPassingCases=outcomes, originalCaseList=roster, fixedInstructionBodies=list(rows.values()),
                    disassembler=pin(javap), disassemblySha256=sha256(result.stdout).hexdigest(),
                    replayedTests=0, directEnvironmentActions=0, sameCandidateNativeOrLiveDiagnostics=False,
                    whole451=False, formalAcceptanceId=None)
    with (out / "manifest.json").open("x") as report:
        report.write(json.dumps(evidence, indent=2) + "\n")
    print(evidence["requirements"], len(built), len(outcomes))


if __name__ == "__main__":
    main()
