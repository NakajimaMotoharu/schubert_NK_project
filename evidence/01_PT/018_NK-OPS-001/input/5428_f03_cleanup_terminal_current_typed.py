"""Use the admitted static profiles on the six changed Cleanup Terminal binaries."""

from datetime import datetime, timezone
from difflib import SequenceMatcher
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__).resolve()
TOOL = runpy.run_path(str(HERE.with_name("5427_f02_terminal_success_reference_pt.py")))
TYPED = runpy.run_path(str(HERE.with_name("5424_f03_expiry_current_typed.py")))
ROOT = HERE.parents[4]
MAIN = TOOL["MAIN"]
pin, git, run, read = (TOOL[key] for key in ("pin", "git", "run", "read"))


def main():
    start = read(next(TOOL["PLAN"].glob("1105_F03Cleanup*")))
    values = start["values"]
    references = values["oracleReferences"]
    assert all(pin(ref["path"]) == ref for ref in references)
    package, focused, profile, history = [read(ref["path"]) for ref in references[1:]]
    core = values["productionCoreMain"]
    current = MAIN.read_bytes()
    assert package["candidateProductionSource"] == core and package["actualExit"] == 0
    assert focused["candidateMain"] == pin(MAIN)
    assert git("rev-parse", "HEAD").decode().strip() == values["source"]
    assert git("show", f"{core}:{MAIN}") == current
    assert not git("diff", "--name-only", core, "--", "pom.xml", "src")
    binaries = package["changedPhysical"]["batch"]
    assert len(binaries) == len(set(binaries)) == 6
    assert all(Path(member).stem.split("$")[0] == MAIN.stem for member in binaries)
    batch = package["privateJars"]["batch"]["artifact"]
    assert pin(batch["path"]) == batch
    rules = ROOT / history["rules"]["path"]
    assert pin(rules)["sha256"] == history["rules"]["sha256"]
    assert pin(history["raw"]["path"]) == history["raw"]
    assert pin(history["terminal"]["path"]) == history["terminal"]
    spot_profile = profile["stages"]["spotbugs"]["command"]
    spot_first = spot_profile[:spot_profile.index("-auxclasspathFromFile") + 1]
    pmd_first = read(history["terminal"]["path"])["command"][:5]
    assert "-effort:max" in spot_first and "-low" in spot_first
    assert tuple(pmd_first[-2:]) == ("net.sourceforge.pmd.cli.PmdCli", "check")
    metadata = TOOL["H"]
    out = (TOOL["E"] / values["run"]).resolve()
    out.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    with TemporaryDirectory(dir="/dev/shm", prefix="pg40748-") as scratch:
        work = Path(scratch)
        source = work / MAIN.name
        source.write_bytes(current)
        target = work / "cleanup-target.jar"
        physical = {}
        with ZipFile(batch["path"]) as compiled, ZipFile(target, "x") as allowlisted:
            for member in sorted(binaries):
                data = compiled.read(member)
                physical[member] = sha256(data).hexdigest()
                allowlisted.writestr(member, data)
        assert physical == read(focused["sourceProofs"][1]["path"])["physical"]
        deps = work / "deps"
        dependencies = metadata["make_classpath"](package["privateJars"], deps)
        specify = TOOL["JSPECIFY"]
        aux = work / "spotbugs-classpath.txt"
        aux.write_text(f"{deps}\n{specify}\n")
        spot = out / "spotbugs.xml"
        pmd = out / "pmd.xml"
        steps = {
            "spotbugs": run("spotbugs", [*spot_first, aux, "-output", spot, target], out, work),
            "pmd": run("pmd", [*pmd_first, "-d", source, "--rulesets", rules, "--use-version",
                               "java-25", "--aux-classpath", os.pathsep.join(map(str, (
                                   deps, target, specify, TOOL["JAVA"].parent.parent / "lib/jrt-fs.jar",
                               ))), "--no-cache", "--format", "xml", "--report-file", pmd], out, work),
        }
    spot_root = ET.parse(spot)
    class_names = [c.get("class") for c in spot_root.iter("ClassStats")]
    expected = {member.removesuffix(".class").replace("/", ".") for member in physical}
    complete = len(class_names) == len(expected) and set(class_names) == expected
    spot_counts = {kind: len(list(spot_root.iter(kind)))
                   for kind in ("BugInstance", "Error", "MissingClass")}
    sites = TYPED["pmd_sites"]
    current_sites = sites(pmd, MAIN.name)
    historical_sites = sites(Path(history["raw"]["path"]), MAIN.name)
    old = git("show", f'{history["productionCore"]}:{MAIN}')
    equal_blocks = SequenceMatcher(None, old.splitlines(), current.splitlines(), autojunk=False)
    equal_lines = {a + offset + 1: b + offset + 1
                   for a, b, size in equal_blocks.get_matching_blocks() for offset in range(size)}
    unchanged_sites = 0
    for (rule, begin, start_col, end, end_col, cls, method), count in historical_sites.items():
        first, last = int(begin), int(end)
        if any(equal_lines.get(i) != equal_lines.get(first, -1) + i - first
               for i in range(first, last + 1)):
            continue
        mapped = (rule, str(equal_lines[first]), start_col, str(equal_lines[last]), end_col, cls, method)
        unchanged_sites += min(count, current_sites[mapped])
    okay = (steps["spotbugs"]["actualExit"] == 0 and complete and not any(spot_counts.values())
            and steps["pmd"]["actualExit"] == (4 if current_sites else 0))
    report = dict(
        actualExit=0 if okay else 1, core=core, source=values["source"], startEvent=start["eventId"],
        target=pin(MAIN), runner=pin(HERE), startedAtUTC=started,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), physical=physical,
        permittedAux=dependencies, classNames=sorted(class_names), spotbugsCounts=spot_counts,
        spotbugsClassStatsComplete=complete, pmdRaw=current_sites.total(),
        pmdProcessingErrors=0, pmdSuppressed=0,
        oldBatchRawAtThisFile=historical_sites.total(), sameRuleAndUnchangedCoordinates=unchanged_sites,
        pmdReviewed=0, pmdUnclassified=current_sites.total(), pmdApplicable=None,
        steps=steps, reports=[pin(spot), pin(pmd)], fixedRules=pin(rules), heldOperations=0,
        productCases=0, wholeF03=False, whole451=False, formalDelta=0,
    )
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(dict(exits={key: step["actualExit"] for key, step in steps.items()},
               classes=len(class_names), spot=spot_counts, pmd=report["pmdRaw"],
               unchangedCoordinates=unchanged_sites))
    return report["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
