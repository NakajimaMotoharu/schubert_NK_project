"""Check the changed exchange owner and record analyzer terminals before inspecting reports."""
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(content):
    return hashlib.sha256(content).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, data):
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    g = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1401_*.json"))
    group = json.loads(g.read_bytes())
    ctx = group["values"]
    refs = ctx["oracleReferences"]
    assert all(pin(Path(item["path"])) == item for item in refs)
    owner, prior_scope, old_types = [json.loads(Path(row["path"]).read_bytes()) for row in refs[1:4]]
    assert owner["source"] == ctx["productionCoreMain"] and owner["scopedCoverageComplete"]
    assert old_types["source"] == prior_scope["source"] == owner["beforeSource"]
    target_pin = owner["currentPhysical"]
    target = Path(target_pin["path"])
    assert pin(target) == target_pin
    class_root = next(p for p in target.parents if p.name == "classes")
    relative_target, = owner["differentPhysical"]
    assert class_root / relative_target == target
    main_pin, = [item for item in owner["inputs"] if item["path"].endswith("/ApiMetricHttpHandler.java")]
    main = Path(main_pin["path"])
    assert pin(main) == main_pin

    work = Path("../pgpt-runs/PG379").resolve() / ctx["run"]
    work.mkdir(mode=0o700)
    typed_aux = work / "aux-classes"
    aux_classes = sorted(old_types["generatedPhysical"], key=lambda x: x["classPath"])
    assert len(aux_classes) == len(list(class_root.rglob("*.class"))) == 30
    for ref in aux_classes:
        path = ref["classPath"]
        if path == relative_target:
            continue
        original = class_root / path
        assert pin(original)["sha256"] == ref["sha256"]
        staged = typed_aux / path
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, staged)
    assert len(list(typed_aux.rglob("*.class"))) == 29
    held = {"TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec", "WebStartupException"}
    auxiliary = []
    for ref in prior_scope["allowedAuxiliaryInventories"]:
        artifact = Path(ref["artifact"]["path"])
        assert pin(artifact) == ref["artifact"]
        with zipfile.ZipFile(artifact) as jar:
            names = sorted(name for name in jar.namelist() if name.endswith(".class"))
        assert len(names) == len(set(names)) == ref["physicalFiles"]
        assert sha("\n".join(names).encode()) == ref["inventorySha256"]
        assert not any(Path(name).stem.split("$", 1)[0] in held for name in names)
        auxiliary.append(artifact)
    assert len(auxiliary) == 15
    aux_file = work / "spotbugs-aux.txt"
    aux_file.write_text("\n".join(map(str, [typed_aux, *auxiliary])) + "\n")
    source_file = work / "pmd-source.txt"
    source_file.write_text(str(main.resolve()) + "\n")

    ops = Path(refs[1]["path"]).parent.parent
    known = json.loads(next(ops.glob("PG40880*/manifest.json")).read_bytes())
    sp_cp = known["steps"]["spotbugs"]["command"][3]
    pmd_cp = known["steps"]["pmd"]["command"][2]
    tc = Path("../toolchain").resolve()
    java = tc / "jdk-25.0.4/bin/java"
    tool_jars = [Path(v) for v in (sp_cp + ":" + pmd_cp).split(":")]
    assert all(p.is_relative_to(tc) and p.is_file() for p in tool_jars)

    def run(label, values):
        command = list(map(str, values))
        started = utc()
        result = subprocess.run(command, env={"PATH": f"{java.parent}:/usr/bin:/bin", "LANG": "C.UTF-8"},
                                capture_output=True, timeout=45, check=False)
        (work / f"{label}.stdout").write_bytes(result.stdout)
        (work / f"{label}.stderr").write_bytes(result.stderr)
        step = dict(command=command, actualExit=result.returncode,
                    startedAtUTC=started, terminalAtUTC=utc(), stdoutSha256=sha(result.stdout),
                    stderrSha256=sha(result.stderr))
        write(work / f"{label}-terminal.json", step)
        return step

    spot_xml = work / "spotbugs.xml"
    sb_end = run("spotbugs", [java, "-Xmx1g", "-cp", sp_cp, "edu.umd.cs.findbugs.FindBugs2",
                             "-effort:max", "-low", "-xml:withMessages", "-exitcode",
                             "-auxclasspathFromFile", aux_file, "-output", spot_xml, target])
    pmd_xml = work / "pmd.xml"
    pmd_end = run("pmd", [java, "-cp", pmd_cp, "net.sourceforge.pmd.cli.PmdCli", "check",
                          "--file-list", source_file, "--rulesets", Path(refs[4]["path"]).resolve(),
                          "--use-version", "java-25", "--aux-classpath",
                          ":".join(map(str, [class_root, *auxiliary, java.parents[1] / "lib/jrt-fs.jar"])),
                          "--no-cache", "--format", "xml", "--report-file", pmd_xml])
    sb = ET.parse(spot_xml).getroot()
    declared = [item.text for item in sb.findall("./Project/Jar")]
    classes = [item.get("class") for item in sb.findall(".//ClassStats")]
    assert declared == [str(target)] and classes == [relative_target.removesuffix(".class").replace("/", ".")]
    sb_counts = dict(findings=len(sb.findall(".//BugInstance")), errors=len(sb.findall(".//Error")),
                     missing=len(sb.findall(".//MissingClass")))
    pmd = ET.parse(pmd_xml).getroot()
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    files = pmd.findall("p:file", ns)
    assert all(Path(item.get("name")).resolve() == main.resolve() for item in files)
    rows = [{"rule": item.attrib["rule"], "line": int(item.attrib["beginline"]),
             "column": int(item.attrib["begincolumn"])}
            for f in files for item in f.findall("p:violation", ns)]
    configuration_errors = len(pmd.findall("p:error", ns)) + len(pmd.findall("p:configerror", ns))
    receipts = sb_end["actualExit"] in (0, 1) and not sb_counts["errors"] and not sb_counts["missing"]
    receipts = receipts and pmd_end["actualExit"] in (0, 4) and not configuration_errors
    out = ops / ctx["run"]
    out.mkdir()
    for xml in (spot_xml, pmd_xml):
        shutil.copyfile(xml, out / xml.name)
    write(out / "manifest.json", dict(
        source=owner["source"], startEvent=group["eventId"], actualExit=0 if receipts else 1,
        terminalAtUTC=utc(), target=target_pin, sourceInput=main_pin, scopeProof=refs[1],
        auxiliarySameBytePhysical=29, auxiliaryJarCount=15, targetClasses=classes,
        spotBugs=dict(**sb_counts, process=sb_end, report=pin(out / spot_xml.name)),
        pmd=dict(findings=rows, processingErrors=configuration_errors, process=pmd_end,
                 report=pin(out / pmd_xml.name)),
        analyzerToolArtifacts=[pin(p) for p in sorted(set(tool_jars))],
        testsRepeated=0, compilerRepeated=0, priorAnalyzersRepeated=0, realExternalOperations=0,
        formalDelta=0, wholeF03=False, whole451=False,
    ))
    print(sb_end["actualExit"], sb_counts, pmd_end["actualExit"], rows)
    raise SystemExit(0 if receipts else 1)


if __name__ == "__main__":
    main()
