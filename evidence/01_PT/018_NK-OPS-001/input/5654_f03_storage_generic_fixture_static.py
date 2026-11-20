"""Verify the added Storage fixture with the established typed quality tools."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5653_f02_storage_generic_edge_pt.py")))
JAVA, JUNIT, NULLABILITY, OPS = (H[key] for key in ("JAVA", "JUNIT", "NULLABILITY", "OPS"))
pin, checked, read, write, run, git = (H[k] for k in ("pin", "checked", "read", "write", "run", "git"))
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def main():
    raw = next(OPS.glob("PG41294-*/manifest.json"))
    unit = read(raw)
    assert unit["actualExit"] == 0 and unit["examinedCases"] == 8
    test = checked(unit["testInputs"][0])
    assert git("show", f'{unit["source"]}:{test}') == test.read_bytes()
    artifact = checked(unit["exactPackagedMain"])
    old = read(next(OPS.glob("PG41264-*/manifest.json")))["stages"]
    out = OPS / "PG41296-f03-storage-generic-edge-typed-v1"
    out.mkdir()
    report = out.resolve()
    toolchain = JAVA.parents[2]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-storage-edge-static-") as work:
        root = Path(work)
        compiled = root / "classes"
        with ZipFile(artifact) as jar:
            for name, obj in unit["actualMainClassSha256"].items():
                path = compiled / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(jar.read(name))
                assert pin(path)["sha256"] == obj
        cp = os.pathsep.join(map(str, (compiled, JUNIT, NULLABILITY)))
        steps = {
            "compile": run([JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                            "-proc:none", "-cp", cp, "-d", compiled, test.resolve()], root, out, "compile"),
            "format": run([JAVA, "-jar", toolchain / "google-java-format-1.36.1-all-deps.jar",
                           "--dry-run", "--set-exit-if-changed", test.resolve()], root, out, "format"),
        }
        assert all(step["actualExit"] == 0 for step in steps.values())
        check = run([JAVA, "-jar", toolchain / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                     "-c", "tools/quality/static/checkstyle.xml", "-f", "xml", test],
                    Path.cwd(), out, "checkstyle")
        steps["checkstyle"] = check
        assert check["actualExit"] == 0
        checkstyle = XML.parse(Path(check["stdout"]["path"])).getroot()
        assert len(checkstyle.findall("file")) == 1 and not checkstyle.findall(".//error")
        sb = old["spotbugs"]["command"][:13]
        sb[10] = cp
        sb[12] = str(report / "spotbugs.xml")
        tests = sorted(compiled.rglob("StorageFailureGraphTest*.class"))
        assert len(tests) == 1
        steps["spotbugs"] = run([*sb, *tests], Path.cwd(), out, "spotbugs")
        listing = root / "inputs.txt"
        listing.write_text(str(test.resolve()) + "\n")
        pmd = old["pmd"]["command"][:6]
        steps["pmd"] = run([*pmd, listing, "--rulesets", "tools/quality/static/pmd.xml",
                           "--use-version", "java-25", "--aux-classpath", f"{JAVA.parents[1]}/lib/jrt-fs.jar:{cp}",
                           "--no-cache", "--format", "xml", "--report-file", report / "pmd.xml"],
                          Path.cwd(), out, "pmd")
        binary_sha = pin(tests[0])["sha256"]
    spotbugs = XML.parse(report / "spotbugs.xml").getroot()
    pmd = XML.parse(report / "pmd.xml").getroot()
    assert steps["spotbugs"]["actualExit"] in (0, 1) and steps["pmd"]["actualExit"] in (0, 4)
    assert not spotbugs.findall(".//MissingClass") + spotbugs.findall(".//Error")
    assert not pmd.findall("p:error", NS) + pmd.findall("p:configerror", NS) + pmd.findall("p:suppressedviolation", NS)
    spots = [node.attrib["type"] for node in spotbugs.findall(".//BugInstance")]
    findings = [dict(name=row.attrib["rule"], line=row.attrib["beginline"])
                for row in pmd.findall("p:file/p:violation", NS)]
    write(out / "manifest.json", dict(
        actualExit=int(bool(spots or findings)), source=unit["source"], core=unit["core"],
        unit=pin(raw), test=pin(test), compiledTestSha256=binary_sha, checkstyleFindings=0,
        spotbugsFindings=spots, pmdFindings=findings, testInvocations=0,
        commands=steps, staticOutput=[pin(report / name) for name in ("pmd.xml", "spotbugs.xml")],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), whole451=False, formalDelta=0))
    print(spots, findings)


if __name__ == "__main__":
    main()
