"""Check approved class responsibility inside API/Web-to-Storage module edges."""

import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
PLAN, OPS, TOOL, JAVA, ARCH, SLF, MODULES, P = (
    H[k] for k in ("PLAN", "OPS", "TOOL", "JAVA", "ARCH", "SLF", "MODULES", "P"))
VALUE = P + "storage.FileReference"
CASES = {
    "001": ("api.application.UseCase", VALUE, True),
    "002": ("api.domain.Value", VALUE + "[]", True),
    "003": ("web.application.Facade", VALUE, True),
    "004": ("web.domain.View", VALUE + "[]", True),
    "005": ("api.storage.Adapter", VALUE, False),
    "006": ("web.storage.Adapter", VALUE, False),
    "007": ("batch.file.Adapter", VALUE, False),
    "008": ("api.application.Service", P + "api.storage.Adapter", False),
    "009": ("web.application.Presenter", P + "web.storage.Adapter", False),
}
OUTCOMES = {
    "before": "PG40432-f02-application-domain-storage-before-v1",
    "after": "PG40434-f02-application-domain-storage-after-v1",
}


def main(mode):
    assert mode in OUTCOMES
    start = json.loads(next(PLAN.glob("857_*")).read_bytes())
    work = start["values"]
    pin, git, sha, execute = (H[key] for key in ("pin", "git", "sha", "execute"))
    ordered = work["oracleReferences"]
    assert all(pin(Path(item["path"])) == item for item in ordered[2:])
    document = git("show", f"{work['canonicalDesignSource']}:{ordered[2]['path']}").decode()
    assert "Controller、application/domain、Protocolからstorageへの依存を禁止する" in document
    source = work["source"] if mode == "before" else git("rev-parse", "HEAD").decode().strip()
    evidence = git("show", f"{source}:{TOOL}")
    assert (sha(evidence) == ordered[1]["sha256"]) == (mode == "before")
    assert all(pin(path)["sha256"] == val for path, val in H["PINS"].items())
    sources = {module: {P + module + ".AuditMarker":
                       'static { System.setProperty("nk.archunit.canary.initialized", "true"); }'}
               for module in MODULES}
    sources["storage"][VALUE] = ""
    for name, dependency, _ in CASES.values():
        sources[name.split(".", 1)[0]][P + name] = f"public {dependency} input;"
    expected = {(P + name, type_.removesuffix("[]")) for name, type_, forbidden in CASES.values()
                if forbidden}
    out = OPS / OUTCOMES[mode]
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-arch-business-file-edge-") as name:
        root = Path(name)
        files = []
        for records in sources.values():
            for fqcn, body in records.items():
                package, _, klass = fqcn.rpartition(".")
                file = root / "fixture" / (fqcn.replace(".", "/") + ".java")
                file.parent.mkdir(exist_ok=True, parents=True)
                file.write_text(f"package {package};\npublic final class {klass} {{ {body} }}\n")
                files.append(file)
        tool_source = root / TOOL.name
        tool_source.write_bytes(evidence)
        tool_out, classes = root / "tool", root / "classes"
        sdk = os.pathsep.join(map(str, (ARCH, SLF)))
        compiler = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        tracked = {}
        for label, command in (
            ("compile-tool", [*compiler, "-cp", sdk, "-d", tool_out, tool_source]),
            ("compile-fixture", [*compiler, "-d", classes, *files]),
        ):
            tracked[label], _ = execute(out, label, command, root)
            assert tracked[label]["actualExit"] == 0
        boards = []
        hashes = {}
        for module, group in sources.items():
            archive = root / (module + ".jar")
            H["archive"](archive, group, classes)
            boards.append(f"{module}={archive}")
            for fqcn in group:
                key = fqcn.replace(".", "/") + ".class"
                hashes[key] = pin(classes / key)["sha256"]
        cp = str(tool_out) + os.pathsep + sdk
        tracked["audit"], report = execute(out, "audit",
                [JAVA, "-cp", cp, "ModuleDependencyAudit", *boards], root)
    rendered = [r.split("\t") for r in report.splitlines()]
    assert ["ARCHUNIT", "1.4.2", str(len(hashes)), str(len(hashes))] in rendered
    expected_mode = set() if mode == "before" else expected
    actual = {(row[2], row[3]) for row in rendered if row[0] == "FINDING" and row[1] == "MODULE_EDGES"}
    assert len(actual) == sum(row[0] == "FINDING" for row in rendered)
    assert actual == expected_mode and tracked["audit"]["actualExit"] == (1 if actual else 0)
    observed = [dict(testId="PT-F02-APPSTORAGE-" + label, origin=P + name,
                     target=type_.removesuffix("[]"), expected=forbidden,
                     actual=(P + name, type_.removesuffix("[]")) in actual)
                for label, (name, type_, forbidden) in CASES.items()]
    data = dict(actualExit=0, mode=mode, source=source, productionCore=work["productionCoreMain"],
                checks=observed, correct=sum(case["expected"] == case["actual"] for case in observed),
                fixturePhysicalHashes=hashes, exactReadPhysicals=len(hashes), toolSha256=sha(evidence),
                receipts=tracked, productTests=0, actualProductClasses=0, fixtureInitializations=0,
                wholeF02Accepted=False, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", data)
    print(pin(out / "manifest.json"), "correct", data["correct"])


if __name__ == "__main__":
    main(sys.argv[1])
