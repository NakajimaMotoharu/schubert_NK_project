"""Keep the proven Protocol build and check the amended artifact and source delta."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import shutil
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML


ROOT = Path(__file__).resolve().parents[4]
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
A = runpy.run_path(str(OPS.parent / "input/5629_f02_current_protocol_archive_rule.py"))
H = runpy.run_path(str(Path(__file__).with_name("107_numeric_validation_order_independent.py")))
git, read, pin, verify, write, JAVA = (H[n] for n in ("git", "read", "pin", "verify", "write", "JAVA"))
P, ARCH, SLF, execute = (A[n] for n in ("P", "ARCH", "SLF", "execute"))
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def main():
    current = next(OPS.glob("PG41304-*/manifest.json"))
    qualified = read(current)
    assert qualified["fullProtocol"] and qualified["ordinaryTests"] == 171 and qualified["jarPhysicalCount"] == 176
    source = qualified["source"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    artifacts = {kind: verify(qualified[kind]) for kind in
                 ("localJar", "originalCoverageXml", "originalExec", "spotbugsXml")}
    retain = ROOT.parent / "pgpt-runs/PG379/PG41306-protocol-numeric-retained-v1"
    retain.mkdir(mode=0o700)
    for label, path in artifacts.items():
        dest = retain / (label + path.suffix)
        shutil.copyfile(path, dest)
        assert pin(dest)["sha256"] == qualified[label]["sha256"]
    previous = read(next(OPS.glob("PG41290-*/manifest.json")))
    out = OPS / "PG41306-protocol-numeric-current-quality-v1"
    out.mkdir()
    architecture = A["H"]
    tool = architecture["TOOL"]
    audience = sorted(set(architecture["MODULES"]) - {"protocol"})
    assert len(audience) == 5
    core = ROOT / "src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/codec/FieldCodec.java"
    unit = ROOT / "src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecTest.java"
    stages = {}
    scope = [core, unit]
    pmd_template = read(next(OPS.glob("PG41264-*/manifest.json")))["stages"]["pmd"]["command"]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-numeric-quality-") as path:
        scratch = Path(path)
        frozen = scratch / tool.name
        frozen.write_bytes(git("show", f"{source}:{tool}"))
        assert not git("diff", "--name-only", previous["source"], source, "--", str(tool))
        lib = os.pathsep.join(map(str, (ARCH, SLF)))
        staged = scratch / "auditor"
        strict = [JAVA.with_name("javac"), "--release", "25", "-Werror", "-Xlint:all", "-proc:none"]
        stages["auditor"], _ = execute(out, "auditor", [*strict, "-cp", lib, "-d", staged, frozen], scratch)
        anchors = []
        for module in audience:
            anchor = scratch / module / "UnrelatedAnchor.java"
            anchor.parent.mkdir()
            anchor.write_text(f"package {P}{module}; public final class UnrelatedAnchor {{}}\n")
            anchors.append(anchor)
        stages["anchors"], _ = execute(out, "anchors", [*strict, "-d", scratch / "classes", *anchors], scratch)
        assert all(stage["actualExit"] == 0 for stage in stages.values())
        args = [f"protocol={retain / 'localJar.jar'}"]
        for module in audience:
            jar = scratch / (module + ".jar")
            architecture["archive"](jar, [P + module + ".UnrelatedAnchor"], scratch / "classes")
            args.append(f"{module}={jar}")
        stages["dependency"], report = execute(out, "dependency", [JAVA, "-cp",
            f"{staged}{os.pathsep}{lib}", "ModuleDependencyAudit", *args], scratch)
        assert stages["dependency"]["actualExit"] == 0
        tools = JAVA.parents[2]
        stages["style"], _ = execute(out, "style", [JAVA, "-jar",
            tools / "static-gates-20261015/checkstyle-14.3.0-all.jar",
            "-c", ROOT / "tools/quality/static/checkstyle.xml", "-f", "xml", *scope], ROOT)
        styles = XML.parse(Path(stages["style"]["stdout"]["path"])).getroot()
        assert len(styles.findall("file")) == 2 and not styles.findall(".//error")
        assert stages["style"]["actualExit"] == 0
        roster = scratch / "pmd-inputs.txt"
        roster.write_text("\n".join(map(str, scope)) + "\n")
        pmd_target = out / "pmd-changed.xml"
        junit = tools / "junit-platform-console-standalone-1.13.4.jar"
        jspecify = tools / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
        aux = os.pathsep.join(map(str, [JAVA.parents[1] / "lib/jrt-fs.jar",
                                      retain / "localJar.jar", junit, jspecify]))
        args = [*pmd_template[:6], roster, "--rulesets", ROOT / "tools/quality/static/pmd.xml",
                "--use-version", "java-25", "--aux-classpath", aux, "--no-cache",
                "--format", "xml", "--report-file", pmd_target]
        stages["pmd"], _ = execute(out, "pmd", args, ROOT)
        assert stages["pmd"]["actualExit"] in (0, 4)
    rows = [line.split("\t") for line in report.splitlines()]
    assert ["ARCHUNIT", "1.4.2", "181", "181"] in rows
    assert {line[1]: int(line[2]) for line in rows if line[0] == "MODULE"} == {
        "protocol": 176, **dict.fromkeys(audience, 1)}
    rules = {line[1]: int(line[2]) for line in rows if line[0] == "RULE"}
    assert rules == previous["verdicts"] == dict.fromkeys(architecture["RULES"], 0)
    edges = next(line[1:] for line in rows if line[0] == "INSPECTED")
    pmd = XML.parse(pmd_target).getroot()
    assert not pmd.findall("p:error", NS) + pmd.findall("p:configerror", NS) + pmd.findall("p:suppressedviolation", NS)
    found = [dict(rule=v.attrib["rule"], path=Path(f.attrib["name"]).name, line=int(v.attrib["beginline"]))
             for f in pmd.findall("p:file", NS) for v in f.findall("p:violation", NS)]
    write(out / "manifest.json", dict(
        actualExit=0, source=source, core=source, run=out.name, qualified=pin(current),
        rawPmdFindings=found, checkstyleFindings=0, dependencyRuleFindings=rules,
        dependencyEdges=int(edges[0]), bytecodeCalls=int(edges[1]), archivedProtocolClasses=176,
        otherModuleAnchors=5, sourceInputs=list(map(pin, scope)), productTestsReplayed=0,
        wholeF02=False, wholeF03=False, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), steps=stages,
        retained={p.name: pin(p) for p in sorted(retain.iterdir())}, pmdReport=pin(pmd_target)))
    print(rules, edges, found)


if __name__ == "__main__":
    main()
