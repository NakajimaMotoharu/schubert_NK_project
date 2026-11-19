"""Check SS311 library HTTP types without loading product or synthetic classes."""

import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

COMMON = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
CASES = (
    ("031", "protocol", "ClientRequest", "java.net.http.HttpRequest", True),
    ("032", "protocol", "ServerExchange", "com.sun.net.httpserver.HttpExchange", True),
    ("033", "storage", "ClientResponse", "java.net.http.HttpResponse<?>", True),
    ("034", "storage", "ServerHandle", "com.sun.net.httpserver.HttpServer", True),
    ("035", "protocol", "GeneralUri", "java.net.URI", False),
    ("036", "storage", "DirectoryPath", "java.nio.file.Path", False),
    ("037", "api", "LocalListener", "com.sun.net.httpserver.HttpExchange", False),
)
NAMES = {
    "before": "PG40198-f02-library-http-before-v1",
    "after": "PG40200-f02-library-http-after-v1",
}


def main(phase):
    audit, pin, git, sha = (COMMON[key] for key in ("TOOL", "pin", "git", "sha"))
    start_path = next(COMMON["PLAN"].glob("667_F02*"))
    start = json.loads(start_path.read_bytes())["values"]
    baseline, design = start["oracleReferences"]
    authority = git("show", f"{start['canonicalDesignSource']}:{design['path']}")
    assert sha(authority) == design["sha256"]
    assert "HTTP model".encode() in authority and "HTTP/DB model".encode() in authority
    assert all(pin(path)["sha256"] == digest for path, digest in COMMON["PINS"].items())
    source = git("rev-parse", "HEAD").decode().strip()
    audit_source = git("show", f"{source}:{audit}")
    original = phase == "before"
    assert (sha(audit_source) == baseline["sha256"]) == original
    out = COMMON["OPS"] / NAMES[phase]
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-library-http-") as directory:
        work = Path(directory)
        (work / audit.name).write_bytes(audit_source)
        launcher = COMMON["JAVA"]
        javac = [launcher.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        sdk = os.pathsep.join(map(str, (COMMON["ARCH"], COMMON["SLF"])))
        compile_tool, _ = COMMON["execute"](
            out, "tool-compile", [*javac, "-cp", sdk, "-d", work / "tool", work / audit.name], work
        )
        assert compile_tool["actualExit"] == 0

        owners = {module: {} for module in COMMON["MODULES"]}
        for module, names in owners.items():
            names[COMMON["P"] + module + ".OwnedCanary"] = (
                'static { System.setProperty("nk.archunit.canary.initialized", "true"); }'
            )
        tests = []
        for test, module, typename, java_type, expected in CASES:
            origin = COMMON["P"] + module + "." + typename
            owners[module][origin] = f"public {java_type} member;"
            tests.append(dict(testId="PT-F02-ARCH-" + test, origin=origin,
                              target=java_type.split("<")[0], expected=expected))
        files = []
        physical = {}
        for names in owners.values():
            for name, member in names.items():
                package, _, typename = name.rpartition(".")
                path = work / "fixtures" / (name.replace(".", "/") + ".java")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"package {package};\npublic final class {typename} {{ {member} }}\n")
                files.append(path)
        compile_fixture, _ = COMMON["execute"](
            out, "fixture-compile", [*javac, "-d", work / "classes", *files], work
        )
        assert compile_fixture["actualExit"] == 0
        for module, names in owners.items():
            COMMON["archive"](work / f"{module}.jar", names, work / "classes")
            physical[module] = {
                name: pin(work / "classes" / (name.replace(".", "/") + ".class"))["sha256"]
                for name in names
            }
        audit_receipt, stdout = COMMON["execute"](
            out, "audit", [launcher, "-cp", str(work / "tool") + os.pathsep + sdk, "ModuleDependencyAudit",
                           *(f"{m}={work / (m + '.jar')}" for m in owners)], work
        )
    rows = stdout.splitlines()
    assert "ARCHUNIT\t1.4.2\t13\t13" in rows
    prefix = "FINDING\tFRAMEWORK_FENCES\t"
    for test in tests:
        test["observed"] = prefix + test["origin"] + "\t" + test["target"] in rows
    expected_findings = {
        prefix + test["origin"] + "\t" + test["target"]
        for test in tests if test["expected"] and not original
    }
    assert {line for line in rows if line.startswith("FINDING\t")} == expected_findings
    assert audit_receipt["actualExit"] == (0 if original else 1)
    manifest = dict(actualExit=0, phase=phase, source=source, productionCore=start["productionCoreMain"],
                    auditSha256=sha(audit_source), tests=tests, physical=physical,
                    receipts={"tool-compile": compile_tool, "fixture-compile": compile_fixture,
                              "audit": audit_receipt},
                    matched=sum(test["expected"] == test["observed"] for test in tests),
                    productJars=0, productTests=0, wholeF02Accepted=False,
                    terminalAtUTC=COMMON["timestamp"]())
    path = out / "manifest.json"
    COMMON["dump"](path, manifest)
    print(pin(path), manifest["matched"])


if __name__ == "__main__":
    main(sys.argv[1])
