"""Check named, annotated and compiler-generated nested controller classfiles only."""

import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
PLAN, OPS, TOOL, JAVA, ARCH, SLF, MODULES, P, WEB = (
    H[key] for key in ("PLAN", "OPS", "TOOL", "JAVA", "ARCH", "SLF", "MODULES", "P", "WEB"))
SOURCE = {
    "ReportController": """public final class ReportController {
        public static final class Loader { public java.sql.Connection connection; }
        public static final class Holder {
          public static final class Deep {
            public long fileSize(java.nio.channels.FileChannel file) throws java.io.IOException {
              return file.size();
            }
          }
        }
      }""",
    "DisplayEndpoint": """@org.springframework.stereotype.Controller public final class DisplayEndpoint {
        public static final class Dispatcher { public jakarta.jms.Message message; }
      }""",
    "JsonHandler": """@org.springframework.web.bind.annotation.RestController public final class JsonHandler {
        public java.util.function.Predicate<java.nio.file.Path> create() {
          return new java.util.function.Predicate<java.nio.file.Path>() {
            public boolean test(java.nio.file.Path path) { return java.nio.file.Files.exists(path); }
          };
        }
      }""",
    "AppController": """public final class AppController {
        public static final class Presenter {
          public void show(SafeFacade facade, java.io.OutputStream out) throws java.io.IOException {
            facade.send();
            out.write(7);
          }
        }
      }""",
    "BusinessFacade": """public final class BusinessFacade {
        public static final class Adapter { public jakarta.jms.Message message; }
      }""",
}
NESTED = {
    "PT-F02-NEST-001": ("ReportController$Loader", ("java.sql.Connection",)),
    "PT-F02-NEST-002": ("ReportController$Holder$Deep", ("java.nio.channels.FileChannel",)),
    "PT-F02-NEST-003": ("DisplayEndpoint$Dispatcher", ("jakarta.jms.Message",)),
    "PT-F02-NEST-004": ("JsonHandler$1", ("java.nio.file.Files",)),
    "PT-F02-NEST-005": ("AppController$Presenter", ()),
    "PT-F02-NEST-006": ("BusinessFacade$Adapter", ()),
}
NAMES = {
    "before": "PG40402-f02-controller-nested-baseline-v1",
    "after": "PG40404-f02-controller-nested-qualified-v1",
}


def main(mode):
    assert mode in NAMES
    start = json.loads(next(PLAN.glob("836_*")).read_bytes())
    work = start["values"]
    git, sha, pin = (H[k] for k in ("git", "sha", "pin"))
    assert all(pin(path)["sha256"] == expected for path, expected in H["PINS"].items())
    core = work["productionCoreMain"]
    source = work["source"] if mode == "before" else git("rev-parse", "HEAD").decode().strip()
    candidate = git("show", f"{source}:{TOOL}")
    assert not git("diff", "--name-only", work["source"], source, "--", "src")
    if mode == "before":
        assert sha(candidate) == work["oracleReferences"][1]["sha256"]
    expected = {}
    for test, name, _, targets, _ in H["CASES"]:
        expected["PT-F02-ARCH-" + test] = (WEB + name, set(targets))
    expected.update({test: (WEB + name, set(targets)) for test, (name, targets) in NESTED.items()})
    out = OPS / NAMES[mode]
    out.mkdir()
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-nested-classfiles-") as directory:
        work_dir = Path(directory)
        inputs = work_dir / "src"
        java = H["fixture_sources"](inputs)
        for name, body in SOURCE.items():
            fqcn = WEB + name
            path = inputs / (fqcn.replace(".", "/") + ".java")
            path.write_text("package " + WEB[:-1] + ";\n" + body + "\n")
            assert fqcn not in java
            java[fqcn] = path
        javac = JAVA.with_name("javac")
        test_classes = work_dir / "fixtures"
        tool_classes = work_dir / "tool"
        tool_java = work_dir / TOOL.name
        tool_java.write_bytes(candidate)
        cp = os.pathsep.join(map(str, (ARCH, SLF)))
        compiler = [javac, "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        commands = {
            "tool-compile": [*compiler, "-cp", cp, "-d", tool_classes, tool_java],
            "fixtures-compile": [*compiler, "-d", test_classes, *java.values()],
        }
        for label, cmd in commands.items():
            receipts[label], _ = H["execute"](out, label, cmd, work_dir)
            assert receipts[label]["actualExit"] == 0
        paths = {name: work_dir / (name + ".jar") for name in MODULES}
        actual_names = {p.relative_to(test_classes).as_posix().removesuffix(".class").replace("/", ".")
                        for p in test_classes.rglob("*.class")}
        web = sorted(n for n in actual_names if n.startswith(WEB) or n in H["STUBS"])
        assert all(name in actual_names for name, _ in expected.values())
        class_lists = {module: [P + module + ".KnownValue"] for module in MODULES}
        class_lists["web"].extend(web)
        assert set(n for values in class_lists.values() for n in values) == actual_names
        hashes = {name: pin(test_classes / (name.replace(".", "/") + ".class"))["sha256"]
                  for name in sorted(actual_names)}
        for module in MODULES:
            H["archive"](paths[module], class_lists[module], test_classes)
        cmd = [JAVA, "-cp", os.pathsep.join((str(tool_classes), cp)), "ModuleDependencyAudit",
               *(module + "=" + str(paths[module]) for module in MODULES)]
        receipts["audit"], output = H["execute"](out, "audit", cmd, work_dir)
        assert receipts["audit"]["actualExit"] == 1
    rows = [line.split("\t") for line in output.splitlines()]
    outputs = {(row[2], row[3]) for row in rows if row[0] == "FINDING" and row[1] == "CONTROLLER_BOUNDARY"}
    assert len(outputs) == sum(row[0] == "FINDING" for row in rows)
    assert {row[1]: int(row[2]) for row in rows if row[0] == "MODULE"} == {
        name: len(values) for name, values in class_lists.items()}
    assert ["ARCHUNIT", "1.4.2", str(len(hashes)), str(len(hashes))] in rows
    wanted = {(name, target) for name, targets in expected.values() for target in targets}
    assert outputs <= wanted
    bases = {name for test, (name, _) in expected.items() if test.startswith("PT-F02-ARCH-")}
    assert {row for row in outputs if row[0] in bases} == {row for row in wanted if row[0] in bases}
    if mode == "after":
        assert outputs == wanted
    differences = [dict(testId=test, origin=name, expected=sorted(targets),
                        observed=sorted(target for origin, target in outputs if origin == name),
                        complete=targets == {target for origin, target in outputs if origin == name})
                   for test, (name, targets) in sorted(expected.items())]
    missing = [row["testId"] for row in differences if not row["complete"]]
    record = dict(actualExit=0, source=source, productionCore=core, mode=mode,
                  analyzedPhysical=len(hashes), fixtureClassHashes=hashes, rootDesign=work["canonicalDesignSource"],
                  analyzerReport=receipts["audit"], stages=receipts, originalCanaries=12, nestedCanaries=6,
                  tests=18, sameProduction=not bool(git("diff", "--name-only", core, source, "--", "src")),
                  findings=sorted(map(list, outputs)), missing=missing, cases=differences,
                  allFixtureInitializations=0, realProductJarInputs=0, productTests=0,
                  wholeF02Accepted=False, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", record)
    print(pin(out / "manifest.json"), missing)


if __name__ == "__main__":
    main(sys.argv[1])
