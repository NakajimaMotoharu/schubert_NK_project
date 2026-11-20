"""Run the retained 35 architecture canaries together against the current tool."""

from collections import Counter
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory


INPUT = Path(__file__).parent
H = runpy.run_path(str(INPUT / "5267_f02_controller_archunit_canaries.py"))
NESTED = runpy.run_path(str(INPUT / "5347_f02_nested_controller_canaries.py"))
PROTOCOL = runpy.run_path(str(INPUT / "5351_f02_protocol_file_canaries.py"))
BUSINESS = runpy.run_path(str(INPUT / "5358_f02_application_domain_storage_canaries.py"))
P, WEB, MODULES = (H[key] for key in ("P", "WEB", "MODULES"))
MARKER = 'static { System.setProperty("nk.archunit.canary.initialized", "true"); }'


def write_fixture(root, fqcn, body):
    path = root / (fqcn.replace(".", "/") + ".java")
    path.parent.mkdir(parents=True, exist_ok=True)
    package, _, clazz = fqcn.rpartition(".")
    path.write_text(f"package {package};\npublic final class {clazz} {{ {body} }}\n")
    return path


def inputs(root):
    java = H["fixture_sources"](root)
    for name, body in NESTED["SOURCE"].items():
        fqcn = WEB + name
        path = root / (fqcn.replace(".", "/") + ".java")
        path.write_text("package " + WEB[:-1] + ";\n" + body + "\n")
        java[fqcn] = path
    for module in MODULES:
        for marker in ("Marker", "AuditMarker"):
            name = P + module + "." + marker
            java[name] = write_fixture(root, name, MARKER)
    for _, module, name, body, _, _ in PROTOCOL["CASES"]:
        fqcn = P + module + "." + name
        java[fqcn] = write_fixture(root, fqcn, body)
    name = BUSINESS["VALUE"]
    java[name] = write_fixture(root, name, "")
    for name, dependency, _ in BUSINESS["CASES"].values():
        fqcn = P + name
        java[fqcn] = write_fixture(root, fqcn, f"public {dependency} input;")
    return [java[name] for name in sorted(java)]


def oracle(records):
    nested, protocol, business = records
    assert len(nested["cases"]) == 18 and all(row["complete"] for row in nested["cases"])
    assert protocol["correct"] == 8 and business["correct"] == 9
    retained = [
        *[(row["testId"], "CONTROLLER_BOUNDARY", row["origin"], row["expected"])
          for row in nested["cases"]],
        *[(row["testId"], "FRAMEWORK_FENCES", row["origin"], [row["target"]] if row["expected"] else [])
          for row in protocol["caseChecks"]],
        *[(row["testId"], "MODULE_EDGES", row["origin"], [row["target"]] if row["expected"] else [])
          for row in business["checks"]],
    ]
    hashes = {
        **nested["fixtureClassHashes"],
        **{name: sha for module in protocol["inputPhysical"].values() for name, sha in module.items()},
        **{name.removesuffix(".class").replace("/", "."): sha
           for name, sha in business["fixturePhysicalHashes"].items()},
    }
    assert len(hashes) == 66 and len({test for test, *_ in retained}) == 35
    return retained, hashes


def main():
    def read(path):
        return json.loads(Path(path).read_bytes())

    pin, git, execute, java, tool = (H[key] for key in ("pin", "git", "execute", "JAVA", "TOOL"))
    begin = read(next(H["PLAN"].glob("866_*")))
    work = begin["values"]
    refs = work["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    assert all(pin(path)["sha256"] == sha for path, sha in H["PINS"].items())
    data = git("show", f"{work['source']}:{tool}")
    assert H["sha"](data) == refs[1]["sha256"]
    records = [read(ref["path"]) for ref in refs[3:6]]
    cases, expected_hashes = oracle(records)
    out = H["OPS"] / work["run"]
    out.mkdir()
    sdk = os.pathsep.join(map(str, (H["ARCH"], H["SLF"])))
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    statuses = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-combined-static-") as directory:
        root = Path(directory)
        src, tool_out, fixture_out = root / tool.name, root / "tool", root / "fixture"
        src.write_bytes(data)
        for stage, command in {
            "compile-tool": [*compiler, "-cp", sdk, "-d", tool_out, src],
            "compile-fixture": [*compiler, "-d", fixture_out, *inputs(root / "input")],
        }.items():
            statuses[stage], _ = execute(out, stage, command, root)
            assert statuses[stage]["actualExit"] == 0
        actual_hashes = {}
        module_names = {name: [] for name in MODULES}
        for item in sorted(fixture_out.rglob("*.class")):
            name = item.relative_to(fixture_out).as_posix().removesuffix(".class").replace("/", ".")
            actual_hashes[name] = pin(item)["sha256"]
            module = name.removeprefix(P).split(".", 1)[0] if name.startswith(P) else "web"
            module_names[module].append(name)
        assert actual_hashes == expected_hashes
        boards = []
        for module, names in module_names.items():
            archive = root / (module + ".jar")
            H["archive"](archive, names, fixture_out)
            boards.append(f"{module}={archive}")
        cp = os.pathsep.join((str(tool_out), sdk))
        statuses["audit"], report = execute(out, "audit", [java, "-cp", cp, "ModuleDependencyAudit", *boards], root)

    rows = [row.split("\t") for row in report.splitlines()]
    assert [row for row in rows if row[0] == "ARCHUNIT"] == [["ARCHUNIT", "1.4.2", "66", "66"]]
    assert {row[1]: int(row[2]) for row in rows if row[0] == "MODULE"} == {
        m: len(names) for m, names in module_names.items()}
    findings = [tuple(row[1:]) for row in rows if row[0] == "FINDING"]
    wanted = {(rule, origin, target) for _, rule, origin, expected in cases for target in expected}
    counts = Counter(rule for rule, _, _ in findings)
    reported = {row[1]: int(row[2]) for row in rows if row[0] == "RULE"}
    assert reported == {rule: counts[rule] for rule in H["RULES"]}
    assert len(findings) == len(wanted) and set(findings) == wanted and statuses["audit"]["actualExit"] == 1
    results = [
        dict(testId=test, rule=rule, origin=origin, expected=expected,
             actual=sorted(t for r, o, t in findings if (r, o) == (rule, origin)))
        for test, rule, origin, expected in cases
    ]
    record = dict(actualExit=0, toolSource=work["source"], productionCore=work["productionCoreMain"],
                  toolSha256=H["sha"](data), tools={str(path): sha for path, sha in H["PINS"].items()},
                  oracleReferences=refs, statuses=statuses, exactInputPhysical=actual_hashes,
                  rules=reported, cases=results, syntheticMatched=35, actualProductionJarInputs=0,
                  productTestsRun=0, fixtureInitializersRun=0, wholeF02Accepted=False,
                  whole451Accepted=False, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", record)
    print(pin(out / "manifest.json"), sorted(reported.items()))


if __name__ == "__main__":
    main()
