"""Check the closed BUG-3415 source and generated class inputs."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree

ROOT = Path.cwd()
SDK = ROOT.parent / "toolchain"
M2 = SDK / "m2/repository"
JDK = SDK / "jdk-25.0.4"
SPECIFY = M2 / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"


def digest(data):
    return sha256(data).hexdigest()


def pin(p):
    return {"path": str(p), "sha256": digest(p.read_bytes())}


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    scope = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1184_*"))
    s = json.loads(scope.read_text())
    v = s["values"]
    for item in v["oracleReferences"]:
        assert pin(Path(item["path"])) == item
    core = v["productionCoreMain"]
    proof = json.loads(Path(v["oracleReferences"][1]["path"]).read_text())
    assert proof["source"] == core and len(proof["cases"]) == 78
    sources = [p for p in proof["inputs"] if "/src/main/java/" in p["path"]]
    assert len(sources) == 13 and all(pin(Path(p["path"])) == p for p in sources)
    for item in sources:
        assert item["sha256"] == digest(subprocess.check_output(["git", "show", f"{core}:{item['path']}"]))
    tools = json.loads(Path(v["oracleReferences"][2]["path"]).read_text())["stages"]
    out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / v["run"]
    out.mkdir()
    steps, controls = {}, {}
    code = 1
    sb = pmd = None
    raw_pmd = None
    started = utc()
    mvn = SDK / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    assert mvn.is_file()
    env = {"PATH": str(JDK / "bin") + ":" + os.defpath,
           "JAVA_HOME": str(JDK), "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def run(label, options):
        command = [str(x) for x in options]
        res = subprocess.run(command, capture_output=True, timeout=85, env=env)
        steps[label] = {"command": command, "exit": res.returncode,
                        "stdoutSha256": digest(res.stdout), "stderrSha256": digest(res.stderr)}
        return res

    with tempfile.TemporaryDirectory(prefix="pg40800-", dir="/dev/shm") as work:
        tmp = Path(work)
        qp = tmp / "scope"
        cfiles = qp / "target/classes"
        syms = qp / "src/main/java"
        syms.mkdir(parents=True)
        parent = tmp / "pom.xml"
        parent.write_bytes(Path("pom.xml").read_bytes())
        parent_hash = digest(parent.read_bytes())
        assert parent_hash == json.loads(Path(v["oracleReferences"][3]["path"]).read_text())["rootPomSha256"]
        scoped_pom = qp / "pom.xml"
        scoped_pom.write_text("""<project xmlns="http://maven.apache.org/POM/4.0.0">
<modelVersion>4.0.0</modelVersion>
<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>
<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>
<artifactId>timed-recovery-closed-scope</artifactId>
<dependencies><dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency></dependencies>
</project>
""")
        harness_hash = digest(scoped_pom.read_bytes())
        for item in sources:
            source = Path(item["path"])
            target = syms / item["path"].split("/src/main/java/", 1)[1]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        assert len(list(syms.rglob("*.java"))) == 13
        result = run("maven", [mvn, "-o", "-B", "-ntp", "-N", "-X", "-f", scoped_pom,
                               f"-Dmaven.repo.local={M2}", "compile"])
        stream = result.stdout.decode(errors="replace")
        controls = dict(nullAwayError="-Xep:NullAway:ERROR" in stream,
                        jspecify="-XepOpt:NullAway:JSpecifyMode=true" in stream,
                        errorProne="-Xplugin:ErrorProne" in stream,
                        werror="-Werror" in stream,
                        exactlyThirteen="Compiling 13 source files" in stream)
        if result.returncode:
            messages = [x for x in stream.splitlines() if "[ERROR]" in x and ("java:[" in x or "illegal" in x.lower())]
            print("compile exit",result.returncode,messages[-8:])
        class_entries = {}
        if result.returncode==0 and all(controls.values()):
            class_entries = {str(p.relative_to(cfiles)): digest(p.read_bytes())
                             for p in cfiles.rglob("*.class")}
            package = "dev/codex/schubert/nk/batch/monitoring/"
            roots = {Path(p["path"]).stem for p in sources}
            assert class_entries and all(p.startswith(package) and
                                         Path(p).stem.split("$", 1)[0] in roots for p in class_entries)
            aux = tmp / "spotbugs-aux.txt"
            aux.write_text(str(SPECIFY) + "\n")
            tool_cp = tools["spotbugs"]["command"][3]
            assert all(Path(jar).is_file() and Path(jar).is_relative_to(SDK) for jar in tool_cp.split(":"))
            sb_report = out / "spotbugs.xml"
            sb_exec = run("spotbugs", [JDK/"bin/java", "-Xmx1g", "-cp", tool_cp,
                       "edu.umd.cs.findbugs.FindBugs2", "-effort:max", "-low", "-xml:withMessages",
                       "-exitcode", "-auxclasspathFromFile", aux, "-output", sb_report, cfiles])
            if sb_report.exists():
                root = ElementTree.parse(sb_report).getroot()
                sb = dict(findings=len(root.findall("BugInstance")),errors=len(root.findall(".//Error")),
                          missing=len(root.findall(".//MissingClass")),report=pin(sb_report))
            pmd_cp = tools["pmd"]["command"][2]
            assert all(Path(jar).is_file() and Path(jar).is_relative_to(SDK) for jar in pmd_cp.split(":"))
            pmd_report = out / "pmd.xml"
            pmd_exec = run("pmd", [JDK/"bin/java", "-cp", pmd_cp, "net.sourceforge.pmd.cli.PmdCli",
                      "check", "-d", syms, "--rulesets", ROOT/"tools/quality/static/pmd.xml",
                      "--use-version", "java-25", "--aux-classpath", f"{cfiles}:{SPECIFY}:{JDK/'lib/jrt-fs.jar'}",
                      "--no-cache", "--format", "xml", "--report-file", pmd_report])
            if pmd_report.exists():
                proot = ElementTree.parse(pmd_report).getroot()
                ns = {"p": proot.tag.partition("}")[0].removeprefix("{")}
                raw_pmd = [{"source": Path(f.attrib["name"]).name, "line": row.attrib["beginline"],
                            "rule": row.attrib["rule"], "message": (row.text or "").strip()}
                           for f in proot.findall("p:file", ns) for row in f.findall("p:violation", ns)]
                pmd = dict(raw=len(raw_pmd), processingErrors=len(proot.findall("p:error", ns)),
                           suppressed=len(proot.findall("p:suppressedviolation", ns)), report=pin(pmd_report))
            if sb and pmd and sb_exec.returncode in (0,1) and pmd_exec.returncode in (0,4):
                code = 0
    info = dict(actualExit=code,source=core,startEvent=s["eventId"],startedAtUTC=started,terminalAtUTC=utc(),
                sources=sources,rootPomSha256=parent_hash,harnessPomSha256=harness_hash,
                compilerControls=controls,steps=steps,exactLocalClassFiles=class_entries,spotbugs=sb,pmd=pmd,
                pmdFindings=raw_pmd,analyzerProductJarInputs=0,heldClassfilesRead=0,productTestsReexecuted=0,
                wholeF03=False,whole451=False,formalDelta=0)
    manifest = out/"manifest.json"
    manifest.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n")
    print(code,len(class_entries),sb,pmd)
    if raw_pmd:
        from collections import Counter
        print(dict(Counter(x["rule"] for x in raw_pmd)))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
