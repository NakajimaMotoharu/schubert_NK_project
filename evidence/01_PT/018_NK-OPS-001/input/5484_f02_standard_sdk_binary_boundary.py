"""Measure the public ABI and direct class dependencies of three qualified SDK owners."""
import hashlib
import json
import os
import re
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def run(command, cwd):
    env = os.environ.copy()
    for key in ("CLASSPATH", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
        env.pop(key, None)
    env["LC_ALL"] = "C"
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
                            timeout=30, check=True)
    assert not result.stderr, result.stderr
    return dict(command=list(map(str, command)), exitCode=result.returncode, stdout=result.stdout)


pmo = Path("documents/400_PGPT/470_PMO")
group_path = next(pmo.glob("601_*/1328_*"))
group = json.loads(group_path.read_bytes())
ctx = group["values"]
for receipt in ctx["oracleReferences"]:
    assert pin(Path(receipt["path"])) == receipt
raw = json.loads(Path(ctx["oracleReferences"][1]["path"]).read_bytes())
assert raw["currentCore"] == ctx["productionCoreMain"] and raw["actualExit"] == 0
release = Path("/home/mini/codex/project1/work/toolchain/jdk-25.0.4")
working = Path("/home/mini/codex/project1/work/pgpt-runs/PG379/PG40904-f03-standard-sdk-owners-current-51-raw-v1")
roles = {"ApiStandardMetricSource": "api",
         "BatchStandardMetricSource": "batch",
         "WebStandardMetricSource": "web"}
mode_owners = {"api": (), "batch": ("MonitoringModePolicy",), "web": ("HttpMetricContract",)}
class_files = {Path(row["path"]).stem: row for row in raw["chosenClassFiles"]}
assert class_files.keys() == roles.keys()
selected = []
for name, module in roles.items():
    class_file = working / (name + ".class")
    assert not class_file.is_symlink() and pin(class_file) == class_files[name]
    assert struct.unpack(">IHH", class_file.read_bytes()[:8]) == (0xCAFEBABE, 0, 69)
    package = f"dev.codex.schubert.nk.{module}.monitoring."
    owner = package + name
    # SS311/351 owner boundary and the pre-fix published API.
    expected_abi = [
        f"public final class {owner} implements java.lang.AutoCloseable {{",
        f"public {owner}();", "descriptor: ()V",
        "public void bind(java.lang.String);", "descriptor: (Ljava/lang/String;)V",
        "public java.lang.String scrape(java.lang.String);",
        "descriptor: (Ljava/lang/String;)Ljava/lang/String;",
        "public void close();", "descriptor: ()V", "}",
    ]
    api = run([str(release / "bin/javap"), "-public", "-s", str(class_file)], working)
    observed_abi = [line.strip() for line in api["stdout"].splitlines()
                    if line.strip() and not line.startswith("Compiled from")]
    assert observed_abi == expected_abi, (name, observed_abi)
    edges = run([str(release / "bin/jdeps"), "--no-recursive", "-verbose:class", "-filter:none",
                 str(class_file)], working)
    dependencies = {}
    for line in edges["stdout"].splitlines():
        if line[:3] != "   " or " -> " not in line:
            continue
        source, arrow, binary, resolved = re.split(r"\s+", line.strip(), maxsplit=3)
        assert arrow == "->" and source == owner
        assert binary not in dependencies
        dependencies[binary] = resolved
    jdk = {cls for cls, location in dependencies.items() if location == "java.base"}
    private_project = {cls for cls in dependencies if cls.startswith("dev.codex.schubert.nk.")}
    sdk = {cls for cls in dependencies if cls.startswith("io.micrometer.")}
    assert "java.lang.AutoCloseable" in jdk and "java.util.Optional" in jdk
    assert all(cls.startswith("java.") for cls in jdk)
    expected_project = (name.removesuffix("Source") + "s", *mode_owners[module])
    assert private_project == {package + target for target in expected_project}
    # The fixed role binder's first parameter is MeterRegistry, not its concrete subtype.
    assert sdk == {"io.micrometer.core.instrument.MeterRegistry",
                   "io.micrometer.core.instrument.binder.jvm.JvmGcMetrics",
                   "io.micrometer.prometheusmetrics.PrometheusConfig",
                   "io.micrometer.prometheusmetrics.PrometheusMeterRegistry"}
    assert dependencies.keys() == jdk | private_project | sdk
    assert all(dependencies[cls] == "not found" for cls in private_project | sdk)
    selected.append(dict(module=module, input=class_files[name], classFileMajor=69,
                         publicAbi=api, classDependencies=edges, jdk=sorted(jdk),
                         sameModule=sorted(private_project), directSdk=sorted(sdk)))

result = dict(
    actualExit=0, source=ctx["productionCoreMain"], wbs="WBS-F02-a", startEvent=group["eventId"],
    startDocument=pin(group_path), terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    relatesTo=["SYS-002", "SYS-007", "SS311", "SS342", "SS351"],
    toolchain=pin(release / "release"), qualifiedInput=ctx["oracleReferences"][1],
    unitOrMavenReruns=0, projectOrSdkJarsAnalyzed=0, testAdded=0, formalDelta=0,
    wholeBuild=False, runtimeVerified=False, selected=selected,
    priorToolAttempts=[
        dict(exitCode=1, phase="API expected direct SDK dependencies"),
        dict(exitCode=1, phase="Batch expected same-module dependencies"),
    ], bug="BUG-3423", horizontalReview="YKT-2743", productChanged=False)
out = Path(ctx["oracleReferences"][1]["path"]).parent.parent / ctx["run"]
out.mkdir()
(out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
