"""Record effective strict compiler settings on the two current Batch repository changes."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile


HERE = Path(__file__).resolve()
BASE = runpy.run_path(str(HERE.with_name("5419_f03_outbox_nullaway_maven.py")))
INPUT = runpy.run_path(str(HERE.with_name("5417_f02_expiry_audit_jdbc_pt.py")))
sha, read, git = (BASE[k] for k in ("sha", "read", "git"))
MAVEN, JDK, TOOLS = (BASE[k] for k in ("MAVEN", "JDK", "TOOLS"))
BATCH = Path("src/schubert-nk-batch/src/main/java")


def main():
    stage = read(next(BASE["PLAN"].glob("1129_F03Batch*")))
    group = stage["values"]
    references = group["oracleReferences"]
    assert all(INPUT["proof"](x["path"]) == x for x in references)
    package, expiry, cleanup, previous_spotbugs, typed = (read(x["path"]) for x in references[1:])
    assert previous_spotbugs["actualExit"] == 0
    actual_compiler = next(BASE["OPS"].glob("PG40700-*/manifest.json"))
    baseline_ref = INPUT["proof"](actual_compiler)
    assert baseline_ref["sha256"] == "af7cf767170d6d09b5abf3e25d2ff3617836dd91d7100fc784e3e45958c869e7"
    baseline = read(actual_compiler)
    assert baseline["actualExit"] == 0 and all(baseline["controls"].values())
    core = group["productionCoreMain"]
    assert package["candidateProductionSource"] == typed["core"] == core
    assert git("rev-parse", "HEAD").decode().strip() == group["source"]
    assert not git("diff", "--name-only", core, "--", "src", "pom.xml")
    root_pom = git("show", f"{core}:pom.xml")
    assert sha(root_pom) == baseline["rootPomSha256"]
    assert INPUT["proof"](MAVEN)["sha256"] == baseline["mavenBinarySha256"]
    assert INPUT["proof"](JDK / "bin/javac")["sha256"] == baseline["jdkBinarySha256"]
    sources = [expiry["candidateMain"], cleanup["candidateMain"]]
    assert {Path(x["path"]).name for x in sources} == {
        "CleanupTerminalRepository.java", "ExpiryAuditRepository.java"
    }
    batch = package["privateJars"]["batch"]["artifact"]
    assert INPUT["proof"](batch["path"]) == batch
    with ZipFile(batch["path"]) as jar:
        expected = {name: sha(jar.read(name)) for name in jar.namelist()
                    if name.endswith(".class") and Path(name).stem.split("$")[0] in {
                        "CleanupTerminalRepository", "ExpiryAuditRepository"
                    }}
    assert len(expected) == 13
    out = BASE["OPS"] / group["run"]
    out.mkdir()
    begin = datetime.now(timezone.utc).isoformat()
    with TemporaryDirectory(dir="/dev/shm", prefix="pg40764-") as directory:
        loc = Path(directory)
        home = loc / "home"
        home.mkdir()
        scope = loc / "scope"
        (loc / "pom.xml").write_bytes(root_pom)
        dep_root = loc / "filtered"
        classes = INPUT["make_classpath"](package["privateJars"], dep_root)
        assert classes == typed["permittedAux"] and len(classes) == 16
        dep_jar = loc / "allowed-dependencies.jar"
        with ZipFile(dep_jar, "x") as zipper:
            for name in sorted(classes):
                zipper.write(dep_root / name, name)
        for entry in sources:
            path = Path(entry["path"])
            body = git("show", f"{core}:{path}")
            assert sha(body) == entry["sha256"] and path.read_bytes() == body
            target = scope / "src/main/java" / path.relative_to(BATCH)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        marker = "  </dependencies>"
        injected_dependency = f"""    <dependency>
      <groupId>dev.codex.pgpt</groupId><artifactId>closed-batch-aux</artifactId><version>1</version>
      <scope>system</scope><systemPath>{dep_jar}</systemPath>
    </dependency>
"""
        pom = scope / "pom.xml"
        pom.write_text(BASE["HARNESS_POM"].replace("pgpt-outbox-nullaway-scope", "pgpt-batch-two-nullaway-scope")
                       .replace(marker, injected_dependency + marker))
        cmd = list(map(str, (MAVEN, "-o", "-B", "-ntp", "-N", "-X", "-f", pom,
                             f'-Dmaven.repo.local={TOOLS / "m2/repository"}', "compile")))
        proc = subprocess.run(cmd, cwd=scope, capture_output=True, timeout=80,
                              env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
                                   "HOME": str(home), "JAVA_HOME": str(JDK), "MAVEN_SKIP_RC": "true",
                                   "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={loc}"})
        stdout = proc.stdout.decode("utf-8", errors="replace")
        terminal = datetime.now(timezone.utc).isoformat()
        compiler_args = next((line for line in stdout.splitlines()
                              if line.lstrip().startswith("[DEBUG] -d ") and "-Xep:NullAway:ERROR" in line), "")
        controls = {
            "errorProneActuallyInCompilerArgs": "-Xplugin:ErrorProne" in compiler_args,
            "nullAwayAsError": "-Xep:NullAway:ERROR" in compiler_args,
            "jspecifyConfigured": "-XepOpt:NullAway:JSpecifyMode=true" in compiler_args,
            "nullAwayArtifactResolved": "nullaway-0.14.1.jar" in compiler_args,
            "warningsAsErrors": "-Werror" in compiler_args,
            "exactTwoCompiled": "Compiling 2 source files" in stdout,
            "mavenBuildSuccessful": "BUILD SUCCESS" in stdout,
        }
        folder = scope / "target/classes"
        physical = {str(p.relative_to(folder)): sha(p.read_bytes()) for p in folder.rglob("*.class")}
        assert set(physical).issubset(expected)
        exit_okay = proc.returncode == 0 and all(controls.values()) and set(physical) == set(expected)
        if not exit_okay:
            errors = [line for line in stdout.splitlines() if line.startswith("[ERROR]")]
            flags = [line for line in stdout.splitlines()
                     if "Command line options:" in line or re.match(r"\[DEBUG\].*-Xep:", line)]
            excerpt = [*errors[:18], *flags[-3:]]
            (out / "diagnostics.txt").write_text("\n".join(excerpt) + "\n")
        result = dict(
            actualExit=0 if exit_okay else 1, mavenExit=proc.returncode, run=group["run"],
            source=group["source"], productionCore=core, startEvent=stage["eventId"], command=cmd,
            beginUTC=begin, terminalAtUTC=terminal, controls=controls, physical=physical,
            exactPackagedClassBytes=sum(physical.get(k) == v for k, v in expected.items()),
            sourceInputs=sources, aux=classes, sourceCount=2, rootPomSha256=sha(root_pom),
            harnessPomSha256=sha(pom.read_bytes()), stdoutSha256=sha(proc.stdout),
            stderrSha256=sha(proc.stderr), tests=0, heldOperations=0, wholeF03=False,
            whole451=False, formalDelta=0, references=[*references, baseline_ref],
        )
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print({k: result[k] for k in ("actualExit", "mavenExit", "controls", "exactPackagedClassBytes")})
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
