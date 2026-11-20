"""Bind the archive audit output to the installed JDK signatures and existing source allowlist."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import runpy
import subprocess


C = runpy.run_path(str(Path(__file__).with_name("5606_f02_controller_file_constructors_post.py")))
OPS, JAVAP, pin, load = (C[k] for k in ("OPS", "JAVAP", "pin", "load"))
FILE_BACKED = ("java.util.zip.ZipFile", "java.util.jar.JarFile")
STREAMS = ("java.util.zip.ZipInputStream", "java.util.jar.JarInputStream")
SIGNATURES = {
    ZIP: (6, {"java.lang.String", "java.io.File"}) for ZIP in FILE_BACKED
} | {stream: (2, {"java.io.InputStream"}) for stream in STREAMS}


def main():
    before_path, before = load("PG41218")
    after_path, after = load("PG41220")
    assert before["newlyMissed"] == 6 and after["newlyMissed"] == 0
    assert before["expectedFindings"] == after["expectedFindings"] == 6
    assert before["productionCore"] == after["productionCore"]
    assert after["previousScopedCanaryReruns"] == 23 and after["previousScopedFindings"] == 13
    for path, content in ((before_path, before), (after_path, after)):
        assert pin(path.with_name("audit.stdout.txt")) == content["stages"]["audit"]["stdout"]
    raw = after_path.with_name("audit.stdout.txt").read_text().splitlines()
    facts = Counter((line.split("\t")[1], line.split("\t")[3])
                    for line in raw if line.startswith("FINDING\t"))
    assert sum(facts.values()) == 19
    assert {entry: count for entry, count in facts.items() if entry[1] in FILE_BACKED} == {
        (kind, archive): 1 for kind in ("CONTROLLER_BOUNDARY", "FRAMEWORK_FENCES") for archive in FILE_BACKED
    }
    assert facts["FRAMEWORK_FENCES", "java.util.Scanner"] == facts["FRAMEWORK_FENCES", "java.io.PrintWriter"] == 1
    commands = []
    for name, (total, first) in SIGNATURES.items():
        cmd = [str(JAVAP), "-public", name]
        completed = subprocess.run(cmd, capture_output=True, check=True, timeout=20)
        constructors = re.findall(r"(?m)^  public "+re.escape(name)+r"\(([^)]*)\)",
                                  completed.stdout.decode())
        actual = {sig.split(", ", 1)[0] for sig in constructors}
        assert len(constructors) == total and actual == first
        commands.append(dict(command=cmd, actualExit=completed.returncode, constructorCount=total,
                             firstParameterTypes=sorted(actual), stdoutSha256=C["sha256"](completed.stdout).hexdigest()))
    known, allowed = load("PG41100")
    for row in allowed["controllerSourcePins"]:
        assert pin(Path(row["path"])) == row
    changed_api_names = re.compile(r"\b(?:ZipFile|JarFile|Scanner|PrintWriter)\b")
    protocol_root = "src/schubert-nk-protocol/src/main/java"
    primaries = subprocess.check_output(["git", "ls-files", protocol_root], text=True, timeout=12).splitlines()
    sources = [Path(path) for path in primaries if path.endswith(".java")]
    assert len(sources) > 150
    assert not subprocess.check_output(["git", "diff", "--name-only", after["productionCore"],
                                        after["source"], "--", protocol_root], timeout=12)
    inputs = sources + [Path(row["path"]) for row in allowed["controllerSourcePins"]]
    observations = [str(p) for p in inputs if changed_api_names.search(p.read_text())]
    assert not observations
    outcome = dict(actualExit=0, source=after["source"], productionCore=after["productionCore"],
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(), inputs=[pin(before_path), pin(after_path), pin(known)],
                   signatures=commands, newCanaries=12, inheritedCases=23, findingsActual=19,
                   protocolSourceCount=len(sources), controllerSourceCount=len(allowed["controllerSourcePins"]),
                   productSourceMentions=observations, productJarsRead=0,
                   actualArchiveOpens=0, productCasesExecuted=0, formalDelta=0, wholeF02=False)
    out = OPS/"PG41222-f02-archive-owner-independent-v1"
    out.mkdir()
    path = out/"manifest.json"
    with path.open("x") as file:
        json.dump(outcome, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(path), len(sources), len(allowed["controllerSourcePins"]), sum(facts.values()))


if __name__ == "__main__":
    main()
