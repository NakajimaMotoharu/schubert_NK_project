"""Run the Root compiler configuration on the admitted Range subset and collect raw PMD."""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


prior = runpy.run_path(str(Path(__file__).with_name("5619_range_unit_ascii.py")))
BIN, OPS, MAIN = (prior[key] for key in ("BIN", "OPS", "MAIN"))
check, pin, read, sha = (prior["helpers"][key] for key in ("check", "pin", "read", "sha"))
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)


def tag(name):
    return f"{{{NS}}}{name}"


def element(parent, name, value=None):
    child = ET.SubElement(parent, tag(name))
    child.text = value
    return child


def main():
    plan, = Path("documents/400_PGPT/470_PMO").glob("601_*/1637_*.json")
    start = read(plan)["values"]
    for ref in start["oracleReferences"]:
        assert pin(Path(ref["path"])) == ref
    _, root_pom, historical, historical_static, green, _ = [
        Path(ref["path"]) for ref in start["oracleReferences"]
    ]
    unit, precedent = read(green), read(historical)
    assert unit["source"] == start["productionCoreMain"] and unit["actualExit"] == 0
    package_info = MAIN.with_name("package-info.java")
    assert pin(package_info)["sha256"] == precedent["inputHashes"][str(package_info)]
    new_test = Path(unit["testsInput"][0]["path"])
    for path in (MAIN, package_info, new_test, root_pom):
        fixed = subprocess.check_output(["git", "show", f'{unit["source"]}:{path}'], timeout=15)
        assert fixed == path.read_bytes()
    root = ET.parse(root_pom).getroot()
    compiler = next(node for node in root.findall(f".//{tag('plugin')}")
                    if node.findtext(tag("artifactId")) == "maven-compiler-plugin")
    serialized = ET.tostring(compiler)
    assert sha(serialized) == precedent["rootCompilerSha256"]
    properties = root.find(tag("properties"))
    required = ("maven.compiler.release", "project.build.sourceEncoding", "error-prone.version",
                "nullaway.version")
    pmd_source = read(historical_static)["stages"]["pmd"]["command"]
    assert pmd_source[3:6] == ["net.sourceforge.pmd.cli.PmdCli", "check", "--file-list"]
    tc = BIN.parent.parent.resolve()
    maven = tc/"m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    repo = tc/"m2/repository"
    junit = unit["junit"]["path"]
    jspecify = repo/"org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
    assert pin(jspecify)["sha256"] == precedent["dependencies"][str(jspecify)]
    pmd_rules = Path("tools/quality/static/pmd.xml").resolve()
    rules_frozen = subprocess.check_output(["git", "show", f'{unit["source"]}:{pmd_rules.relative_to(Path.cwd())}'],
                                           timeout=15)
    assert sha(rules_frozen) == pin(pmd_rules)["sha256"]
    out = (OPS/"PG41208-f03-range-current-nullaway-pmd-v1").resolve()
    out.mkdir()
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-range-current-static-") as temp:
        scratch = Path(temp)
        component = scratch/"src/main/java"/prior["DIR"]
        component.mkdir(parents=True)
        for path in (MAIN, package_info):
            (component/path.name).write_bytes(path.read_bytes())
        subset = ET.Element(tag("project"))
        for key, value in (("modelVersion", "4.0.0"), ("groupId", "dev.codex.schubert.quality"),
                           ("artifactId", "pgpt-range-closed-source-subset"), ("version", "1")):
            element(subset, key, value)
        props = element(subset, "properties")
        for key in required:
            element(props, key, properties.findtext(tag(key)))
        dep = element(element(subset, "dependencies"), "dependency")
        for key, value in (("groupId", "org.jspecify"), ("artifactId", "jspecify"), ("version", "1.0.1")):
            element(dep, key, value)
        element(element(subset, "build"), "plugins").append(deepcopy(compiler))
        pom = scratch/"pom.xml"
        ET.ElementTree(subset).write(pom, encoding="utf-8", xml_declaration=True)
        pom_hash = pin(pom)["sha256"]
        command = ["env", f"JAVA_HOME={BIN.parent}", f"PATH={BIN}:/usr/bin:/bin", maven, "-o",
                   "-f", pom, "--no-transfer-progress", f"-Dmaven.repo.local={repo}",
                   "-Dmaven.test.skip=true", "compile"]
        stages["nullaway"], compiled = check(command)
        (out/"nullaway.stdout").write_bytes(compiled.stdout)
        (out/"nullaway.stderr").write_bytes(compiled.stderr)
        assert compiled.returncode == 0, (compiled.stdout[-1800:], compiled.stderr[-1000:])
        classes = scratch/"target/classes"
        physical = sorted(classes.rglob("*.class"))
        actual = {path.name: pin(path)["sha256"] for path in physical if path.name != "package-info.class"}
        assert len(physical) == 6 and len(actual) == 5
        expected = {Path(row["path"]).name: row["sha256"] for row in unit["physical"]}
        listing = out/"sources.txt"
        listing.write_text("".join(str(path.resolve()) + "\n" for path in (MAIN, new_test)))
        report = out/"pmd.xml"
        pmd = [*pmd_source[:6], listing, "--rulesets", pmd_rules, "--use-version", "java-25",
               "--aux-classpath", ":".join(map(str, (BIN.parent/"lib/jrt-fs.jar", classes, jspecify, junit))),
               "--no-cache", "--format", "xml", "--report-file", report]
        stages["pmd"], scanned = check(pmd)
        (out/"pmd.stderr").write_bytes(scanned.stderr)
        assert scanned.returncode in (0, 4), scanned.stderr
        raw = ET.parse(report).getroot()
        sites = []
        errors = []
        suppressions = 0
        for item in raw:
            kind = item.tag.split("}")[-1]
            if kind == "file":
                for site in item:
                    sites.append(dict(source=Path(item.get("name")).name,
                                      rule=site.get("rule"), line=int(site.get("beginline"))))
            elif kind == "suppressedviolation":
                suppressions += 1
            elif kind in ("error", "configerror"):
                errors.append(kind)
        canary_name = "PgptNullAwayContractCanary.java"
        canary = component/canary_name
        canary.write_text("package dev.codex.schubert.nk.web.media;\n"
                          "final class PgptNullAwayContractCanary { String reject() { return null; } }\n")
        stages["staticCanary"], canary_result = check(command)
        canary_hits = sum(b"[NullAway]" in line and b"returning @Nullable" in line
                          for line in canary_result.stdout.splitlines())
        assert canary_result.returncode and canary_hits >= 1 and canary_name.encode() in canary_result.stdout
    outputs = sorted(p for p in out.iterdir() if p.is_file())
    data = dict(run=out.name, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                source=unit["source"], actualExit=0 if not errors and not sites and not suppressions else 1,
                exactRootCompilerSha256=sha(serialized), subsetPomSha256=pom_hash,
                sourceInputs=list(map(pin, (MAIN, package_info, new_test, root_pom, pmd_rules))),
                compiledPhysicalMatchesUnit={name: value == expected[name] for name, value in actual.items()},
                stagedCanaryExpectedNonzero=canary_result.returncode,
                stagedCanaryNullAwayMessages=canary_hits, rawPmdSites=sites, pmdErrors=errors,
                rawPmdSuppressed=suppressions, stages=stages, outputs=list(map(pin, outputs)),
                executedProductPt=0, fullMavenWebPackage=False, wholeF03=False,
                whole451=False, formalDelta=0)
    dest = out/"manifest.json"
    with dest.open("x") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(dest), sites, errors, "matched", sum(data["compiledPhysicalMatchesUnit"].values()), "canary", canary_hits)
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
