"""Exercise the inherited Maven compiler warning gate without loading product classes."""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write_json(path, value):
    with path.open("x") as out:
        out.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


OUTPUT = Path("evidence/01_PT/018_NK-OPS-001")
PACKAGE = "dev/codex/schubert/nk/quality"
CHILD = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>dev.codex.schubert</groupId>
    <artifactId>schubert-nk</artifactId>
    <version>0.1.0-SNAPSHOT</version>
    <relativePath>../pom.xml</relativePath>
  </parent>
  <artifactId>compiler-warning-control</artifactId>
</project>
"""
API = """package dev.codex.schubert.nk.quality;

final class TextApi {
  static String currentText() {
    return "current";
  }

  @Deprecated
  static String legacyText() {
    return "legacy";
  }
}
"""
CALL = """package dev.codex.schubert.nk.quality;

final class CompilerControl {
  String read() {
    return TextApi.%s();
  }
}
"""


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1428_*.json"))
    group = json.loads(plan.read_bytes())
    scope = group["values"]
    core = scope["productionCoreMain"]
    original_pom = Path("pom.xml")
    assert pin(original_pom) == scope["oracleReferences"][1]
    assert original_pom.read_bytes() == subprocess.check_output(
        ["git", "show", f"{core}:pom.xml"])
    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    work = Path("../pgpt-runs/PG379").resolve() / scope["run"]
    work.mkdir(mode=0o700)
    (work / "pom.xml").write_bytes(original_pom.read_bytes())
    observations = []
    for control, method, expected in (("valid", "currentText", 0), ("warning", "legacyText", 1)):
        project = work / control
        main = project / "src/main/java" / PACKAGE
        main.mkdir(parents=True)
        pom, api, call = project / "pom.xml", main / "TextApi.java", main / "CompilerControl.java"
        pom.write_text(CHILD)
        api.write_text(API)
        call.write_text(CALL % method)
        argv = [str(x) for x in (
            maven, "-o", "-N", "-B", "-ntp", "-X", "-f", pom, f"-Dmaven.repo.local={tc}/m2/repository", "compile")]
        start = utc()
        process = subprocess.run(argv, capture_output=True, env=env, timeout=90, check=False)
        output_path, error_path = project / "maven.stdout", project / "maven.stderr"
        output_path.write_bytes(process.stdout)
        error_path.write_bytes(process.stderr)
        output = process.stdout.decode()
        signals = {
            "defaultCompile": bool(re.search(r"compiler:[^ ]+:compile \(default-compile\)", output)),
            "exactFlagsPresent": all(flag in output for flag in ("-Xlint:all", "-Werror", "-Xep:NullAway:ERROR")),
            "deprecationDiagnostic": bool(re.search(r"CompilerControl\.java:\[5,\d+\].*\[deprecation\].*legacyText", output)),
            "warningRejected": "warnings found and -Werror specified" in output,
            "anyCompilerWarning": bool(re.search(r"^\[WARNING\].*\.java:\[", output, flags=re.MULTILINE)),
        }
        tree = project / "target/classes"
        classfiles = [{**pin(path), "major": int.from_bytes(path.read_bytes()[6:8], "big")}
                      for path in sorted(tree.rglob("*.class"))]
        target_generated = any(Path(row["path"]).name == "CompilerControl.class" for row in classfiles)
        accepted = signals["defaultCompile"] and signals["exactFlagsPresent"] and process.returncode == expected
        if expected == 0:
            accepted = (accepted and not signals["anyCompilerWarning"] and not signals["warningRejected"]
                        and target_generated and len(classfiles) == 2 and all(x["major"] == 69 for x in classfiles))
        else:
            accepted = (accepted and signals["deprecationDiagnostic"] and signals["warningRejected"]
                        and not target_generated)
        record = dict(control=control, expectedExit=expected, actualExit=process.returncode, startedAtUTC=start,
                      terminalAtUTC=utc(), command=argv, inputs=[pin(p) for p in (pom, api, call)],
                      stdout=pin(output_path), stderr=pin(error_path), signals=signals, classfiles=classfiles,
                      diagnostic=[line.strip() for line in output.splitlines()
                                  if "[deprecation]" in line or "warnings found and -Werror specified" in line],
                      accepted=accepted)
        write_json(project / "terminal.json", record)
        observations.append(record)

    result = OUTPUT / "evidence" / scope["run"]
    result.mkdir()
    passed = all(row["accepted"] for row in observations)
    write_json(result / "manifest.json", dict(
        source=core, documentationHead=scope["source"], startEvent=group["eventId"], run=scope["run"],
        testId="PT-F03-COMPILER-001", actualExit=0 if passed else 1, terminalAtUTC=utc(), os="Linux",
        java="25.0.4", maven="3.9.12", tools=[pin(jdk / "bin/javac"), pin(maven)],
        rootPom=pin(original_pom), specification=pin(next(OUTPUT.glob("5533_*.md"))),
        harness=pin(Path(__file__).relative_to(Path.cwd())), controls=observations,
        productMainCompiled=0, productTestsStarted=0, productCoverage=None, realEnvironmentOperations=0,
        wholeF03=False, whole451=False, formalDelta=0))
    print([(row["control"], row["actualExit"], row["accepted"], row["signals"]) for row in observations])
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
