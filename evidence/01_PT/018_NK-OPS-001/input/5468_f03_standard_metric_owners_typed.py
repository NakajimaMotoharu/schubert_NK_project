"""Run typed checks on the three fixed standard SDK owners and their exact local helpers."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
import json
import os
import subprocess
import tempfile


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git_show(source, path):
    return subprocess.check_output(["git", "show", f"{source}:{path}"], timeout=20)


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
group = read(next(plan.glob("1290_*")))
ctx = group["values"]
core = ctx["productionCoreMain"]
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
runs = [next(evidence.glob("PG40874-*/manifest.json")), *sorted(evidence.glob("PG40878-*/manifest.json"))]
previous = [read(path) for path in runs]
assert any(run["source"] != core for run in previous) and all(run["actualExit"] == 0 for run in previous)
sources = [row for run in previous for row in run["productionInputs"]]
assert len(sources) == len({row["path"] for row in sources}) == 20
for row in sources:
    path = Path(row["path"])
    assert pin(path) == row and sha(git_show(core, path)) == row["sha256"]
targets = {row["path"].split("/src/main/java/")[1].removesuffix(".java") + ".class": row["path"]
           for row in sources if row["path"].endswith("StandardMetricSource.java")}
assert len(targets) == 3
deps = previous[0]["runtimeDependencies"]
assert len(deps) == 12 and all(run["runtimeDependencies"] == deps for run in previous)
assert all(pin(Path(row["path"])) == row for row in deps)
prior = read(next(evidence.glob("PG40838-*/manifest.json")))
assert prior["actualExit"] == 0
parent_bytes = git_show(core, "pom.xml")
assert parent_bytes == Path("pom.xml").read_bytes() and sha(parent_bytes) == prior["rootPomSha256"]

tc = Path.cwd().parent / "toolchain"
m2 = tc / "m2/repository"
jdk = tc / "jdk-25.0.4"
mvn = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
steps = {}
out = evidence / ctx["run"]
out.mkdir()
started = datetime.now(timezone.utc).isoformat()


def run(label, *args):
    argv = list(map(str, args))
    env = {"PATH": f"{jdk}/bin:{os.defpath}", "JAVA_HOME": str(jdk), "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    result = subprocess.run(argv, capture_output=True, timeout=90, env=env)
    steps[label] = dict(command=argv, exit=result.returncode, stdoutSha256=sha(result.stdout),
                        stderrSha256=sha(result.stderr))
    return result


with tempfile.TemporaryDirectory(prefix="pg40880-", dir="/dev/shm") as loc:
    tmp = Path(loc)
    root = tmp / "scope"
    java_sources = root / "src/main/java"
    java_sources.mkdir(parents=True)
    (tmp / "pom.xml").write_bytes(parent_bytes)
    dependency_xml = "".join(
        "<dependency><groupId>fixed.sdk</groupId>"
        f"<artifactId>local-sdk-{i}</artifactId><version>1</version><scope>system</scope>"
        f"<systemPath>{escape(row['path'])}</systemPath></dependency>"
        for i, row in enumerate(deps)
    )
    project = root / "pom.xml"
    project.write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>local-standard-sdk-owner-qualification</artifactId>'
        f'<dependencies>{dependency_xml}</dependencies></project>\n'
    )
    for row in sources:
        relative = row["path"].split("/src/main/java/")[1]
        target = java_sources / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(row["path"]).read_bytes())
    compile = run("maven", mvn, "-o", "-B", "-ntp", "-N", "-X", "-f", project,
                  f"-Dmaven.repo.local={m2}", "compile")
    log = compile.stdout.decode(errors="replace")
    controls = {token: token in log for token in (
        "-Xep:NullAway:ERROR", "-XepOpt:NullAway:JSpecifyMode=true", "-Werror", "Compiling 20 source files")}
    classes = root / "target/classes"
    sb = pmd = None
    type_inventory = {}
    status = compile.returncode
    if status == 0 and all(controls.values()):
        class_set = {row["path"].split("/src/main/java/")[1].removesuffix(".java") for row in sources}
        type_inventory = {str(path.relative_to(classes)): sha(path.read_bytes()) for path in classes.rglob("*.class")}
        assert set(targets) <= type_inventory.keys()
        assert all(name.removesuffix(".class").split("$", 1)[0] in class_set for name in type_inventory)
        aux = tmp / "spotbugs-aux.txt"
        aux.write_text("\n".join(row["path"] for row in deps) + "\n")
        sb_report = out / "spotbugs.xml"
        sb_cp = prior["steps"]["spotbugs"]["command"][3]
        assert all(Path(path).is_relative_to(tc) for path in sb_cp.split(":"))
        se = run("spotbugs", jdk / "bin/java", "-Xmx1g", "-cp", sb_cp, "edu.umd.cs.findbugs.FindBugs2",
                 "-effort:max", "-low", "-xml:withMessages", "-exitcode", "-auxclasspathFromFile", aux,
                 "-output", sb_report, classes)
        if sb_report.is_file():
            report = ET.parse(sb_report).getroot()
            found = [node.attrib["class"] for node in report.findall(".//ClassStats")]
            declared = {name.removesuffix(".class").replace("/", ".") for name in type_inventory
                        if not name.endswith("package-info.class")}
            assert [node.text for node in report.findall("./Project/Jar")] == [str(classes)]
            sb = dict(findings=len(report.findall(".//BugInstance")), errors=len(report.findall(".//Error")),
                      missing=len(report.findall(".//MissingClass")), scopeCount=len(found),
                      statsOutsideDeclared=sorted(set(found) - declared),
                      noClassStats=sorted(declared - set(found)), report=pin(sb_report))
        pmd_cp = prior["steps"]["pmd"]["command"][2]
        assert all(Path(path).is_relative_to(tc) for path in pmd_cp.split(":"))
        pmd_report = out / "pmd.xml"
        file_list = tmp / "pmd-targets.txt"
        file_list.write_text("\n".join(str(java_sources / name.removesuffix(".class")) + ".java"
                                        for name in sorted(targets)) + "\n")
        pmd_aux = ":".join([str(classes), *(row["path"] for row in deps), str(jdk / "lib/jrt-fs.jar")])
        pe = run("pmd", jdk / "bin/java", "-cp", pmd_cp, "net.sourceforge.pmd.cli.PmdCli", "check",
                 "--file-list", file_list, "--rulesets", Path.cwd() / "tools/quality/static/pmd.xml",
                 "--use-version", "java-25", "--aux-classpath", pmd_aux, "--no-cache", "--format", "xml",
                 "--report-file", pmd_report)
        if pmd_report.is_file():
            report = ET.parse(pmd_report).getroot()
            ns = {"p": report.tag.partition("}")[0].removeprefix("{")}
            findings = [dict(file=Path(item.attrib["name"]).name, rule=node.attrib["rule"],
                             line=int(node.attrib["beginline"])) for item in report.findall("p:file", ns)
                        for node in item.findall("p:violation", ns)]
            pmd = dict(raw=len(findings), findings=findings, errors=len(report.findall("p:error", ns)),
                       suppressed=len(report.findall("p:suppressedviolation", ns)), report=pin(pmd_report))
        status = 0 if (sb is not None and pmd is not None and not sb["statsOutsideDeclared"]
                       and not sb["noClassStats"] and se.returncode == 0 and pe.returncode in (0, 4)) else 1
    elif status == 0:
        status = 1
    else:
        print("\n".join(x for x in log.splitlines() if "[ERROR]" in x)[-1600:])
    harness = sha(project.read_bytes())
record = dict(actualExit=status, source=core, startEvent=group["eventId"], steps=steps,
              startedAtUTC=started, terminalAtUTC=datetime.now(timezone.utc).isoformat(), controls=controls,
              parentPomSha256=sha(parent_bytes), harnessPomSha256=harness, sourceInputs=sources,
              dependencies=deps, exactPhysical=type_inventory, changedClasses=sorted(targets),
              spotbugs=sb, pmd=pmd, historicalLocalProofs=[pin(path) for path in runs],
              productTestsExecuted=0, heldProductInputs=0, actualExternalOperations=0,
              wholeF03=False, whole451=False, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(status, len(type_inventory), sb, pmd, pin(manifest))
raise SystemExit(status)
