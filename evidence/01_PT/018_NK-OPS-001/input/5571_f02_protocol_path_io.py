"""Check Path method-owner rules with class files whose methods are never executed."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


SERIAL = runpy.run_path(str(Path(__file__).with_name("5393_f02_protocol_serialization.py")))
V, R, H, C, SUPPORT, PREVIOUS = (
    SERIAL[key] for key in ("V", "R", "H", "C", "SUPPORT", "PREVIOUS"))
P = H["P"]
PATH = "java.nio.file.Path"
RULE = "FRAMEWORK_FENCES"

# Names, method bodies and expected disposition are independent of the audit predicates.
CASES = (
    ("protocol.RealPathRead", """
      public java.nio.file.Path inspect(java.nio.file.Path path) throws java.io.IOException {
        return path.toRealPath(java.nio.file.LinkOption.NOFOLLOW_LINKS);
      }""", True),
    ("protocol.WatchEvents", """
      public java.nio.file.WatchKey subscribe(java.nio.file.Path path, java.nio.file.WatchService watcher)
          throws java.io.IOException {
        return path.register(watcher, java.nio.file.StandardWatchEventKinds.ENTRY_CREATE);
      }""", True),
    ("protocol.WatchModifiers", """
      public java.nio.file.WatchKey subscribe(java.nio.file.Path path, java.nio.file.WatchService watcher,
          java.nio.file.WatchEvent.Kind<?>[] events, java.nio.file.WatchEvent.Modifier modifier)
          throws java.io.IOException {
        return path.register(watcher, events, modifier);
      }""", True),
    ("protocol.RealPathReference", """
      public interface Inspect {
        java.nio.file.Path read(java.nio.file.Path path, java.nio.file.LinkOption... options)
            throws java.io.IOException;
      }
      public Inspect factory() { return java.nio.file.Path::toRealPath; }""", True),
    ("protocol.NormalizePath", """
      public java.nio.file.Path value(java.nio.file.Path path) { return path.normalize(); }""", False),
    ("protocol.ResolvePath", """
      public java.nio.file.Path value(java.nio.file.Path path, java.nio.file.Path suffix) {
        return path.resolve(suffix);
      }""", False),
    ("protocol.PathValue", "public java.nio.file.Path value;", False),
    ("storage.AllowedPhysicalPath", """
      public java.nio.file.Path inspect(java.nio.file.Path path) throws java.io.IOException {
        return path.toRealPath();
      }""", False),
)


def prior_sources(root):
    field = C["write_fixture"]
    return (
        [field(root, origin, f"public {target} field;") for _, origin, target, _ in SERIAL["CASES"]]
        + C["inputs"](root) + R["additional_sources"](root) + V["fixture_sources"](root)
        + SUPPORT["fixture"](root) + PREVIOUS["fixtures"](root)
    )


def fixture_owners(root):
    owners = {module: [] for module in H["MODULES"]}
    physical = {}
    for path in sorted(root.rglob("*.class")):
        name = path.relative_to(root).as_posix().removesuffix(".class").replace("/", ".")
        if name in V["STUBS"]:
            continue
        module = ("api" if name == R["ANNOTATION"] else
                  name.removeprefix(P).split(".", 1)[0] if name.startswith(P) else "web")
        owners[module].append(name)
        physical[name] = H["pin"](path)["sha256"]
    return owners, physical


def main(after):
    pin, git, execute = (H[key] for key in ("pin", "git", "execute"))
    start_file, = H["PLAN"].glob("1516_*")
    start = R["read"](start_file)["values"]
    assert all(pin(Path(row["path"])) == row for row in start["oracleReferences"])
    assert all(pin(path)["sha256"] == want for path, want in H["PINS"].items())
    source = git("rev-parse", "HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    prior = Path(start["oracleReferences"][1]["path"])
    old = R["read"](prior)
    past = SUPPORT["published_findings"](prior.with_name("audit.stdout.txt"))
    assert len(past) == 53 and old["matched"] + old["priorControls"] == 82
    out = H["OPS"] / ("PG41064-f02-protocol-path-io-after-v1" if after else start["run"])
    out.mkdir()
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    steps = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-protocol-path-io-") as name:
        root = Path(name)
        fixture = root / "fixtures"
        code = root / tool.name
        code.write_bytes(data)
        sources = [C["write_fixture"](fixture, P + origin, body) for origin, body, _ in CASES]
        if after:
            sources += prior_sources(fixture)
        else:
            sources += [C["write_fixture"](fixture, P + module + ".Anchor", C["MARKER"])
                        for module in H["MODULES"]]
        for key, command in (
            ("compile-tool", [*compiler, "-cp", cp, "-d", root / "tool", code]),
            ("compile-fixture", [*compiler, "-d", root / "binary", *sources]),
        ):
            steps[key], _ = execute(out, key, command, root)
            assert steps[key]["actualExit"] == 0
        owners, physical = fixture_owners(root / "binary")
        if after:
            assert all(physical[key] == value for key, value in old["inputPhysical"].items())
        args = []
        for module, types in sorted(owners.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, types, root / "binary")
            args.append(f"{module}={jar}")
        steps["audit"], raw = execute(out, "audit", [
            java, "-cp", str(root / "tool") + os.pathsep + cp, "ModuleDependencyAudit", *args,
        ], root)
    findings = SUPPORT["published_findings"](out / "audit.stdout.txt")
    expected = {(RULE, P + origin, PATH) for origin, _, prohibited in CASES if prohibited}
    assert findings == (past | expected if after else set()), sorted(findings ^ (past | expected))
    assert steps["audit"]["actualExit"] == int(after)
    assert [line.split("\t")[2:] for line in raw.splitlines() if line.startswith("ARCHUNIT\t")] == [
        [str(len(physical))] * 2
    ]
    checks = [dict(testId=f"PT-F02-PATH-IO-{index:03}", origin=P + origin, target=PATH,
                   expected=prohibited, observed=(RULE, P + origin, PATH) in findings)
              for index, (origin, _, prohibited) in enumerate(CASES, 1)]
    destination = out / "manifest.json"
    H["dump"](destination, dict(actualExit=0 if after else 1, toolSource=source,
                                productionCore=start["productionCoreMain"], toolSourceSha256=H["sha"](data),
                                sourceSpec=pin(Path(__file__)), priorControls=82 if after else 0,
                                priorReceipt=pin(prior), fixtures=checks,
                                matched=sum(row["expected"] == row["observed"] for row in checks),
                                physical=[dict(className=n, sha256=sha) for n, sha in physical.items()],
                                findings=len(findings), steps=steps, productTests=0,
                                productJars=0, fixtureMethodsInvoked=0, filesystemOperationsInvoked=0,
                                wholeF02Accepted=False, whole451Accepted=False,
                                terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(destination))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
