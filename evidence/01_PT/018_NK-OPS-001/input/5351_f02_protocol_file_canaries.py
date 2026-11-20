"""Show whether the existing static module audit detects Protocol-owned file I/O."""

import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
PLAN, OPS, TOOL, JAVA, ARCH, SLF, MODULES, P = (
    H[k] for k in ("PLAN", "OPS", "TOOL", "JAVA", "ARCH", "SLF", "MODULES", "P"))
CASES = (
    ("001", "protocol", "FilesRead", "long size(java.nio.file.Path p) throws java.io.IOException "
     "{ return java.nio.file.Files.size(p); }", "java.nio.file.Files", True),
    ("002", "protocol", "FileStream", "java.io.InputStream stream(String path) throws java.io.IOException "
     "{ return new java.io.FileInputStream(path); }", "java.io.FileInputStream", True),
    ("003", "protocol", "FileChannelCall", "long size(java.nio.channels.FileChannel in) "
     "throws java.io.IOException { return in.size(); }", "java.nio.channels.FileChannel", True),
    ("004", "protocol", "ProviderCall", "void check(java.nio.file.spi.FileSystemProvider source, "
     "java.nio.file.Path path) throws java.io.IOException { source.checkAccess(path); }",
     "java.nio.file.spi.FileSystemProvider", True),
    ("005", "protocol", "PathValue", "String text(java.nio.file.Path p) { return p.toString(); }",
     "java.nio.file.Path", False),
    ("006", "protocol", "BorrowedByteStream", "int read(java.io.InputStream stream) throws java.io.IOException "
     "{ return stream.read(); }", "java.io.InputStream", False),
    ("007", "storage", "LowLevelFile", "long size(java.nio.file.Path p) throws java.io.IOException "
     "{ return java.nio.file.Files.size(p); }", "java.nio.file.Files", False),
    ("008", "batch", "FilePort", "long size(java.nio.file.Path p) throws java.io.IOException "
     "{ return java.nio.file.Files.size(p); }", "java.nio.file.Files", False),
)
NAMES = {"before": "PG40414-f02-protocol-file-before-v1", "after": "PG40416-f02-protocol-file-after-v1"}


def main(mode):
    assert mode in NAMES
    start = json.loads(next(PLAN.glob("842_*")).read_bytes())
    work = start["values"]
    git, pin, sha = (H[k] for k in ("git", "pin", "sha"))
    source = work["source"] if mode == "before" else git("rev-parse", "HEAD").decode().strip()
    assert all(pin(Path(ref["path"])) == ref for ref in work["oracleReferences"][2:])
    design = work["oracleReferences"][2]
    content = git("show", f"{work['canonicalDesignSource']}:{design['path']}").decode()
    assert "Protocolへfilesystem実装を移す方法は採らない" in content
    old_tool = work["oracleReferences"][1]
    candidate = git("show", f"{source}:{TOOL}")
    assert (sha(candidate) == old_tool["sha256"]) == (mode == "before")
    assert all(pin(path)["sha256"] == digest for path, digest in H["PINS"].items())
    refs = []
    payloads = {name: {P + name + ".Marker": 'static { System.setProperty("nk.archunit.canary.initialized", "true"); }'}
                for name in MODULES}
    for label, module, name, text, target, expect in CASES:
        origin = P + module + "." + name
        payloads[module][origin] = text
        refs.append(dict(testId="PT-F02-PROFILE-" + label, origin=origin, target=target, expected=expect))
    output = OPS / NAMES[mode]
    output.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-protocol-file-") as loc:
        workdir = Path(loc)
        fixture = workdir / "fixture"
        sources = []
        for cases in payloads.values():
            for name, body in cases.items():
                java = fixture / (name.replace(".", "/") + ".java")
                java.parent.mkdir(parents=True, exist_ok=True)
                package, _, cls = name.rpartition(".")
                java.write_text(f"package {package};\npublic final class {cls} {{ {body} }}\n")
                sources.append(java)
        audit_java = workdir / TOOL.name
        audit_java.write_bytes(candidate)
        cp = os.pathsep.join(map(str, (ARCH, SLF)))
        compiler = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        classes = workdir / "classes"
        run_tool = workdir / "toolclasses"
        steps = {}
        for label, cmd in (
            ("tool-compile", [*compiler, "-cp", cp, "-d", run_tool, audit_java]),
            ("fixtures-compile", [*compiler, "-d", classes, *sources]),
        ):
            steps[label], _ = H["execute"](output, label, cmd, workdir)
            assert steps[label]["actualExit"] == 0
        hashes = {}
        jars = {}
        for module, cases in payloads.items():
            jar = workdir / (module + ".jar")
            H["archive"](jar, cases, classes)
            hashes[module] = {name: pin(classes / (name.replace(".", "/") + ".class"))["sha256"]
                              for name in cases}
            jars[module] = jar
        steps["audit"], stream = H["execute"](output, "audit",
            [JAVA, "-cp", str(run_tool) + os.pathsep + cp, "ModuleDependencyAudit",
             *(f"{name}={jar}" for name, jar in jars.items())], workdir)
    lines = [row.split("\t") for row in stream.splitlines()]
    assert ["ARCHUNIT", "1.4.2", "14", "14"] in lines
    findings = {(r[2], r[3]) for r in lines if r[0] == "FINDING" and r[1] == "FRAMEWORK_FENCES"}
    assert len(findings) == sum(r[0] == "FINDING" for r in lines)
    assert findings == ({(case["origin"], case["target"]) for case in refs if case["expected"]}
                        if mode == "after" else set())
    assert steps["audit"]["actualExit"] == (1 if findings else 0)
    for case in refs:
        case["observed"] = (case["origin"], case["target"]) in findings
    manifest = dict(actualExit=0, source=source, productionCore=work["productionCoreMain"], phase=mode,
                    exactDesignRoot=work["canonicalDesignSource"], toolSha256=sha(candidate),
                    originalStaticScopeOnly=True, caseChecks=refs, inputPhysical=hashes,
                    correct=sum(case["observed"] == case["expected"] for case in refs),
                    stages=steps, productJarInputs=0, productTests=0, nativeActions=0,
                    wholeF02Accepted=False, terminalAtUTC=H["timestamp"]())
    H["dump"](output / "manifest.json", manifest)
    print(pin(output / "manifest.json"), manifest["correct"])


if __name__ == "__main__":
    main(sys.argv[1])
