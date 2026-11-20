"""Collect the missing typed static evidence for two already tested Java fixtures."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


m = runpy.run_path(str(Path(__file__).with_name("5609_scr012_count_underclaim.py")))
OPS, BIN, check, pin, read = (m[key] for key in ("OPS", "BIN", "check", "pin", "read"))
ROOT = "dev/codex/schubert/nk/"
JDBC = "JdbcFailureGraphOrderTest.java"
USER = "UserListLastPageCountTest.java"
BLOCKED = {"TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec", "WebStartupException"}


def prepare(compiled, sources, sdk):
    compiled.mkdir()
    for dep in sdk:
        with ZipFile(dep) as jar:
            assert all(Path(name).stem.split("$")[0] not in BLOCKED for name in jar.namelist())
    cp = os.pathsep.join(map(str, sdk))
    stage, result = check([BIN/"javac", "--release", "25", "-g", "-Xlint:all", "-Werror",
                           "-proc:none", "-cp", cp, "-d", compiled, *sources])
    assert result.returncode == 0, result.stderr
    return stage


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1652_*.json")
    inputs = read(start)["values"]["oracleReferences"]
    for ref in inputs:
        assert pin(Path(ref["path"])) == ref
    _, jdbc_ref, jdbc_static, user_ref, rules = [Path(row["path"]) for row in inputs]
    j, s, u = (read(path) for path in (jdbc_ref, jdbc_static, user_ref))
    assert j["source"] == s["source"] == u["productionCore"]
    assert j["actualExit"] == s["actualExit"] == u["actualExit"] == 0
    assert s["findings"] == [] and s["errors"] == s["missing"] == 0
    assert pin(jdbc_ref) == s["prior"]
    jdbc_inputs, user_inputs = j["inputSources"], u["mainInputs"]+[u["testSource"]]
    assert Path(jdbc_inputs[-1]["path"]).name == JDBC and Path(user_inputs[-1]["path"]).name == USER
    for ref in jdbc_inputs + user_inputs + j["dependencies"] + u["dependencies"]:
        assert pin(Path(ref["path"])) == ref
    static_pmd, = OPS.glob("PG41208-*/manifest.json")
    pmd = read(static_pmd)["stages"]["pmd"]["command"]
    assert pmd[3:6] == ["net.sourceforge.pmd.cli.PmdCli", "check", "--file-list"]
    ref, = OPS.glob("PG41162-*/manifest.json")
    spotbugs = read(ref)["stagedStatic"]["spotbugs"]["command"][:13]
    assert spotbugs[4] == "edu.umd.cs.findbugs.FindBugs2"
    out = OPS/"PG41228-f03-current-user-jdbc-fixture-static-v1"
    out.mkdir()
    measurements = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-new-fixture-static-") as temporary:
        space = Path(temporary)
        for role, rows, sdk in (("user", user_inputs, u["dependencies"]),
                               ("jdbc", jdbc_inputs, j["dependencies"])):
            classes = space/role
            dependencies = [Path(row["path"]) for row in sdk]
            java = [Path(row["path"]) for row in rows]
            compile_stage = prepare(classes, java, dependencies)
            made = {str(p.relative_to(classes)):pin(p)["sha256"] for p in classes.rglob("*.class")}
            if role == "user":
                assert made == u["compiledPhysical"]
            else:
                sealed = {Path(row["path"]).name:row["sha256"] for row in j["sealedPhysical"]}
                assert {Path(path).name:digest for path,digest in made.items()
                        if "JdbcFailureGraphOrderTest" not in path} == sealed
            file_list = out/(role+"-target.txt")
            file_list.write_text(str(java[-1].resolve())+"\n")
            pmd_xml = out/(role+"-pmd.xml")
            cp = os.pathsep.join(map(str, [classes, *dependencies]))
            pmd_stage, run = check([*pmd[:6], file_list, "--rulesets", rules.resolve(), "--use-version",
                "java-25", "--aux-classpath", f"{BIN.parent}/lib/jrt-fs.jar:{cp}",
                "--no-cache", "--format", "xml", "--report-file", pmd_xml])
            assert run.returncode in (0, 4), run.stderr
            root = ET.parse(pmd_xml).getroot()
            findings = [dict(rule=site.get("rule"), line=int(site.get("beginline")))
                        for site in root.iter() if site.tag.split("}")[-1]=="violation"]
            errors = [site.tag.split("}")[-1] for site in root.iter()
                      if site.tag.split("}")[-1] in {"error","configerror","suppressedviolation"}]
            receipt = dict(compile=compile_stage, inputSources=rows, pmd=pmd_stage, report=pin(pmd_xml),
                           rawPmd=findings, pmdErrorsOrSuppressions=errors, compiledClasses=len(made))
            if role == "user":
                owned = classes/(ROOT+"web/view/UserListLastPageCountTest.class")
                assert owned.is_file()
                report = out/"user-spotbugs.xml"
                spotbugs[10] = cp
                spotbugs[12] = report
                stage, outcome = check([*spotbugs, owned])
                spot = ET.parse(report).getroot()
                receipt["spotbugs"] = dict(stage=stage, report=pin(report),
                    findings=[site.get("type") for site in spot.findall("BugInstance")],
                    errors=len(spot.findall(".//Error")), missing=len(spot.findall(".//MissingClass")))
            else:
                receipt["typedExistingResult"] = pin(jdbc_static)
            measurements[role] = receipt
    typed = measurements["user"]["spotbugs"]
    valid = not typed["findings"] and typed["errors"]==typed["missing"]==typed["stage"]["exit"]==0
    valid = valid and all(not x["rawPmd"] and not x["pmdErrorsOrSuppressions"] for x in measurements.values())
    record = dict(run=out.name, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  source=j["source"], actualExit=0 if valid else 1,
                  evidence=list(map(pin, (start,jdbc_ref,jdbc_static,user_ref,rules,static_pmd))),
                  staticByTest=measurements, dynamicProductTests=0, forbiddenArtifactReads=0,
                  changedProductSources=0, wholeF03=False, whole451=False, formalDelta=0)
    path = out/"manifest.json"
    with path.open("x") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(path), {k:x["rawPmd"] for k,x in measurements.items()}, typed["findings"])
    return record["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
