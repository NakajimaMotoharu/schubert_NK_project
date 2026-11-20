"""Check API repository direction with ordinary synthetic class files."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


INPUT = Path(__file__).parent
COMBINED = runpy.run_path(str(INPUT / "5361_f02_combined_static_boundaries.py"))
H = COMBINED["H"]
BASE = H["P"] + "api."
SERVICE = BASE + "application.audit.AuditService"
CLOCK = "java.time.Clock"
ANNOTATION = "org.springframework.stereotype.Repository"
NESTED = BASE + "support.ReportRepository"
CALL = f"public int read() {{ return {SERVICE}.value(); }}"
CASES = (
    ("001", BASE + "persistence.SqlPort", SERVICE, True),
    ("002", BASE + "monitoring.persistence.LiveCountPort", SERVICE, True),
    ("003", BASE + "security.LoginLedgerRepository", SERVICE, True),
    ("004", BASE + "messaging.outbound.SendLedgerRepository", SERVICE, True),
    ("005", BASE + "support.AnnotatedListPort", SERVICE, True),
    ("006", NESTED + "$Mapper", SERVICE, True),
    ("007", SERVICE, BASE + "security.LoginLedgerRepository", False),
    ("008", BASE + "support.RepositoryFactory", SERVICE, False),
    ("009", BASE + "security.OrdinaryRoute", SERVICE, False),
    ("010", BASE + "security.LowerRepository", CLOCK, False),
)


def additional_sources(root):
    plain = {
        CASES[0][1]: CALL,
        CASES[1][1]: CALL,
        CASES[2][1]: CALL + " public static int fixed() { return 1; }",
        CASES[3][1]: CALL,
        NESTED: "public static final class Mapper { " + CALL + " }",
        SERVICE: f"public static int value() {{ return {CASES[2][1]}.fixed(); }}",
        CASES[7][1]: CALL,
        CASES[8][1]: CALL,
        CASES[9][1]: "public java.time.Clock clock() { return java.time.Clock.systemUTC(); }",
    }
    paths = [COMBINED["write_fixture"](root, name, body) for name, body in plain.items()]
    for name, body in (
        (ANNOTATION, "public @interface Repository {}"),
        (CASES[4][1], f"@{ANNOTATION} public final class AnnotatedListPort {{ {CALL} }}"),
    ):
        path = root / (name.replace(".", "/") + ".java")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"package {name.rpartition('.')[0]};\n{body}\n")
        paths.append(path)
    return paths


def read(path):
    return json.loads(Path(path).read_bytes())


def main(after):
    pin, git, run = (H[key] for key in ("pin", "git", "execute"))
    start = read(next(H["PLAN"].glob("953_*")))
    values = start["values"]
    before_source = values["source"]
    execution_source = git("rev-parse", "HEAD").decode().strip() if after else before_source
    tool = H["TOOL"]
    baseline = git("show", f"{before_source}:{tool}")
    data = git("show", f"{execution_source}:{tool}")
    assert (data != baseline) == after
    assert all(pin(path)["sha256"] == expected for path, expected in H["PINS"].items())
    assert all(pin(Path(ref["path"])) == ref for ref in values["oracleReferences"])
    old_style = read(values["oracleReferences"][1]["path"])
    assert old_style["actualExit"] == 0 and not old_style["wholeF02Accepted"]
    old_run_path = next(H["OPS"].glob("PG40444-*/manifest.json"))
    old_run = read(old_run_path)
    assert old_run["syntheticMatched"] == 35
    design = Path("documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md")
    ss = git("show", values["canonicalDesignSource"] + ":" + str(design))
    assert "repositoryから上位層を呼ばない".encode() in ss
    output = H["OPS"] / ("PG40568-f02-api-repository-direction-after-v1" if after else values["run"])
    output.mkdir()
    sdk = os.pathsep.join(str(H[x]) for x in ("ARCH", "SLF"))
    java = H["JAVA"]
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-repository-scopes-") as tmp:
        root = Path(tmp)
        tool_file = root / tool.name
        tool_file.write_bytes(data)
        inputs = COMBINED["inputs"](root / "input") if after else [
            COMBINED["write_fixture"](root / "input", H["P"] + m + ".Anchor", COMBINED["MARKER"])
            for m in H["MODULES"]
        ]
        inputs += additional_sources(root / "input")
        for tag, command in (
            ("tool", [*compiler, "-cp", sdk, "-d", root / "tool", tool_file]),
            ("fixture", [*compiler, "-d", root / "classes", *inputs]),
        ):
            receipts[tag], _ = run(output, tag, command, root)
            assert receipts[tag]["actualExit"] == 0
        groups = {m: [] for m in H["MODULES"]}
        physical = {}
        for p in (root / "classes").rglob("*.class"):
            name = p.relative_to(root / "classes").as_posix().removesuffix(".class").replace("/", ".")
            physical[name] = pin(p)["sha256"]
            if name == ANNOTATION:
                module = "api"
            else:
                module = name.removeprefix(H["P"]).split(".", 1)[0] if name.startswith(H["P"]) else "web"
            groups[module].append(name)
        archives = []
        for module, names in sorted(groups.items()):
            archive = root / (module + ".jar")
            H["archive"](archive, sorted(names), root / "classes")
            archives.append(f"{module}={archive}")
        receipts["audit"], stdout = run(
            output, "audit",
            [java, "-cp", str(root / "tool") + os.pathsep + sdk, "ModuleDependencyAudit", *archives],
            root,
        )
    rows = [line.split("\t") for line in stdout.splitlines()]
    findings = {tuple(row[1:]) for row in rows if row[0] == "FINDING"}
    assert [row[2:] for row in rows if row[0] == "ARCHUNIT"] == [[str(len(physical))] * 2]
    assert receipts["audit"]["actualExit"] == 1
    expected_prior = {
        (row["rule"], row["origin"], t) for row in old_run["cases"] for t in row["expected"]
    } if after else set()
    if after:
        assert all(physical.get(name) == h for name, h in old_run["exactInputPhysical"].items())
    actual_cases = []
    for test, origin, target, expected in CASES:
        key = ("REPOSITORY_DIRECTION", origin, target)
        actual_cases.append(dict(testId="PT-F02-REPO-" + test, expected=expected,
                                 actual=key in findings, origin=origin, target=target))
    expected_new = {("REPOSITORY_DIRECTION", r["origin"], r["target"])
                    for r in actual_cases if r["expected"]}
    assert not findings.difference(expected_prior | expected_new)
    assert expected_prior.issubset(findings)
    completed = sum(row["actual"] == row["expected"] for row in actual_cases)
    assert completed == (10 if after else 6)
    manifest = output / "manifest.json"
    H["dump"](manifest, dict(
        actualExit=0 if after else 1, source=execution_source, productionCore=values["productionCoreMain"],
        staticToolSha256=H["sha"](data), canonicalSS311=dict(path=str(design), sha256=H["sha"](ss)),
        inputPhysical=physical, receipts=receipts, tests=actual_cases, matched=completed,
        oldControlsVerified=35 if after else 0, rawRuleCounts=Counter(row[0] for row in findings),
        productTests=0, productJars=0, wholeF02Accepted=False,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    ))
    print(pin(manifest), completed, len(physical))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
