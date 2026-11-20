"""Measure the admitted package delta without analyzing the held native agent type."""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5657_f03_storage_exact_static.py")))
ROOT, TOOLS, JAVA, OPS, PLAN = (H[n] for n in ("ROOT", "TOOLS", "JAVA", "OPS", "PLAN"))
git, pin, checked, read, write, run = (H[n] for n in ("git", "pin", "checked", "read", "write", "run"))
MODULE = Path("src/schubert-nk-bootstrap")
HELD_SOURCE_NAME = "FixedNativeCoverageCheckpoint.java"
HELD_PHYSICAL = "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent.class"
RETIRED = "dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmission$1.class"
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def main():
    ctx = read(next(PLAN.glob("1707_*.json")))["values"]
    _, prior_path, static_path, later_path, current_path = map(checked, ctx["oracleReferences"])
    old, initial, later, package = map(read, (prior_path, static_path, later_path, current_path))
    assert old["actualExit"] == initial["actualExit"] == later["actualExit"] == package["actualExit"] == 0
    assert later["raw"]["bootstrap"]["classStats"] == 200 and later["raw"]["bootstrap"]["bugs"] == 0
    stamp = ctx["productionCoreMain"]
    assert git("rev-parse", "HEAD").decode().strip() == ctx["source"]
    assert not git("diff", "--name-only", package["source"], stamp, "--", str(MODULE / "src/main"),
                   str(MODULE / "pom.xml"), "pom.xml")
    scope = git("diff", "--name-only", old["sourceCore"], stamp, "--", str(MODULE / "src/main/java"))
    paths = list(map(Path, scope.decode().splitlines()))
    assert len(paths) == 12 and all(path.name.endswith(".java") for path in paths)
    active_sources = [path for path in paths if path.name != HELD_SOURCE_NAME]
    assert len(active_sources) == 11
    artifact = checked(package["packagedBuild"]["bootstrap"]["artifact"])
    storage = checked(package["packagedBuild"]["storage"]["artifact"])
    earlier = old["physicalClassHashes"]["bootstrap"]
    with ZipFile(artifact) as jar:
        class_paths = [n for n in jar.namelist() if n.endswith(".class")]
        assert len(class_paths) == len(set(class_paths)) == 201
        assert set(earlier) - set(class_paths) == {RETIRED}
        payloads = {name: jar.read(name) for name in class_paths if name != HELD_PHYSICAL}
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    active_changed = sorted(name for name, digest in inventory.items() if earlier.get(name) != digest)
    assert len(earlier) == 200 and len(active_changed) == 13 and len(inventory) - len(active_changed) == 187
    assert HELD_PHYSICAL in class_paths and HELD_PHYSICAL not in inventory
    assert not any(any(text in name for text in ("FingerprintKeyRing", "TemporaryInfrastructureException",
                                               "WebStartupException", "ResponseSnapshotCodec"))
                   for name in class_paths)
    site = later_path.parent / "attempt-02/bootstrap-analysis-v2.pom.xml"
    assert pin(site)["sha256"] == later["evidence"]["attempt-02/bootstrap-analysis-v2.pom.xml"]
    dependencies = [Path(row.text) for row in XML.parse(site).findall(".//{*}systemPath")]
    assert len(dependencies) == 11 and dependencies[-1].name == "current-storage.jar"
    dependencies[-1] = storage
    assert all(path.is_file() for path in dependencies)
    preserve = read(next(OPS.glob("PG41264-*/manifest.json")))["stages"]
    out = OPS / ctx["run"]
    out.mkdir()
    destination = out.resolve()
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-bootstrap-typed-") as scratch:
        room = Path(scratch)
        extract = room / "classes"
        for name, body in payloads.items():
            path = extract / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        sources = []
        for name in active_sources:
            path = room / name.name
            path.write_bytes(git("show", f"{stamp}:{name}"))
            sources.append(path)
        assert not list(extract.rglob("*$PublicAgent.class"))
        style = run([JAVA, "-jar", TOOLS / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                     "-c", ROOT / "tools/quality/static/checkstyle.xml", "-f", "xml", *sources],
                    ROOT, out, "checkstyle")
        stages["checkstyle"] = style
        orig = XML.parse(style["stdout"]["path"]).getroot()
        assert style["actualExit"] == 0 and len(orig.findall("file")) == 11 and not orig.findall(".//error")
        cp = os.pathsep.join(map(str, (extract, *dependencies)))
        spot = preserve["spotbugs"]["command"][:13]
        spot[10], spot[12] = cp, str(destination / "spotbugs.xml")
        stages["spotbugs"] = run([*spot, *[extract / n for n in active_changed]], ROOT, out, "spotbugs")
        manifest = room / "sources.txt"
        manifest.write_text("\n".join(map(str, sources)) + "\n")
        pmd = preserve["pmd"]["command"][:6]
        stages["pmd"] = run([*pmd, manifest, "--rulesets", ROOT / "tools/quality/static/pmd.xml",
                            "--use-version", "java-25", "--aux-classpath", f"{JAVA.parents[1]}/lib/jrt-fs.jar:{cp}",
                            "--no-cache", "--format", "xml", "--report-file", destination / "pmd.xml"],
                           ROOT, out, "pmd")
        source_hashes = {str(a): pin(b)["sha256"] for a, b in zip(active_sources, sources, strict=True)}
    assert stages["spotbugs"]["actualExit"] in (0, 1)
    assert stages["pmd"]["actualExit"] in (0, 4)
    spot = XML.parse(destination / "spotbugs.xml").getroot()
    summary = {k: len(spot.findall(".//" + n)) for k, n in
               (("bugs", "BugInstance"), ("missing", "MissingClass"), ("errors", "Error"))}
    class_names = {el.attrib["class"] for el in spot.findall(".//ClassStats")}
    assert class_names == {name.removesuffix(".class").replace("/", ".") for name in active_changed}
    pmd = XML.parse(destination / "pmd.xml").getroot()
    assert not pmd.findall("p:error", NS) + pmd.findall("p:configerror", NS) + pmd.findall("p:suppressedviolation", NS)
    findings = [dict(owner=Path(row.attrib["name"]).name, rule=value.attrib["rule"],
                     method=value.attrib.get("method", ""), line=int(value.attrib["beginline"]))
                for row in pmd.findall("p:file", NS) for value in row.findall("p:violation", NS)]
    write(out / "manifest.json", dict(
        actualExit=int(bool(any(summary.values()) or findings)), source=ctx["source"], core=stamp,
        run=out.name, oldPhysical=200, physical=201, exactPriorClassBytes=187, staticTargetPhysical=13,
        staticallyHeldPhysical=1, heldTypeBodyOpened=False, retiredGenerated=RETIRED,
        analyzedPhysical=active_changed, analyzedSourceSha256=source_hashes, pmd=pin(destination / "pmd.xml"),
        spotbugs=pin(destination / "spotbugs.xml"), spotbugsCounters=summary, rawPmd=findings,
        checkstyleFindings=0, currentJar=pin(artifact), oldCompiler=pin(prior_path), steps=stages,
        allowedDependencyPins=list(map(pin, dependencies)), actualTests=0,
        backendNativeOperations=0, wholeF03=False, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(summary, findings)


if __name__ == "__main__":
    main()
