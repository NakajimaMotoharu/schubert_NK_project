"""Audit synthetic ImageIO owners without executing their methods."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from zipfile import ZipFile


SAX = runpy.run_path(str(Path(__file__).with_name("5767_f02_sax_file_contract.py")))
H, C, SUPPORT, ARCHIVE, FILELOG, IMAGE = (
    SAX[name] for name in ("H", "C", "SUPPORT", "ARCHIVE", "FILELOG", "IMAGE")
)
PREFIX, CONTROLLER, FENCE = (SAX[name] for name in ("PREFIX", "CONTROLLER", "FENCE"))
IMAGE_PREFIX = "javax.imageio.stream."
DISK = (
    ("FileImageInputStream", "file"),
    ("FileImageOutputStream", "file"),
    ("FileCacheImageInputStream", "input, file"),
    ("FileCacheImageOutputStream", "output, file"),
)
MEMORY = (("MemoryCacheImageInputStream", "input"), ("MemoryCacheImageOutputStream", "output"))
CASES = (
    ("web.synthetic.ImageDiskController", DISK, CONTROLLER, True),
    ("api.messaging.inbound.ImageDiskListener", DISK, FENCE, True),
    ("protocol.ImageDiskSource", DISK, FENCE, True),
    ("web.synthetic.ImageMemoryController", MEMORY, CONTROLLER, False),
    ("api.messaging.inbound.ImageMemoryListener", MEMORY, FENCE, False),
    ("protocol.ImageMemorySource", MEMORY, FENCE, False),
    ("batch.ImageDiskAdapter", DISK, FENCE, False),
)
PROTOCOL_ROSTER = (
    "../pgpt-runs/PG379/PG43018-f02-sax-direct-file-v1/current-protocol-v2/scope-proof.json"
)
PROTOCOL_SHA256 = "2e11940216614fbe48e663fd83400f1fe3cf1cd9fc626214c954aaddb8c0407f"


def body(constructors):
    expressions = ", ".join(
        f"new {IMAGE_PREFIX}{name}({arguments})" for name, arguments in constructors
    )
    return (
        "public Object[] run(java.io.File file, java.io.InputStream input, java.io.OutputStream output)"
        " throws java.io.IOException { return new Object[] { " + expressions + " }; }"
    )


def earlier_sources(scratch, expectations):
    write = C["write_fixture"]
    prior = [
        write(scratch, PREFIX + owner, code)
        for owner, _, code, _, _ in IMAGE["CASES"]
    ]
    expectations.update(
        (rule, PREFIX + owner, target)
        for owner, target, _, rule, deny in IMAGE["CASES"] if deny
    )
    prior.extend(FILELOG["cases"](scratch, FILELOG["CASES"], expectations))
    prior.extend(FILELOG["known"](scratch, expectations))
    for owner, kind, rule, deny in SAX["CASES"]:
        parser = SAX["SAX"]
        prior.append(write(
            scratch, PREFIX + owner,
            f"public void run({parser} parser, {kind} input, org.xml.sax.helpers.DefaultHandler handler)"
            " throws java.io.IOException, org.xml.sax.SAXException { parser.parse(input, handler); }",
        ))
        if deny:
            expectations.add((rule, PREFIX + owner, parser))
    return prior


def protocol_input():
    proof = json.loads(Path(PROTOCOL_ROSTER).read_text())
    artifact = Path(proof["protocolJar"]["path"])
    assert H["pin"](artifact)["sha256"] == PROTOCOL_SHA256
    with ZipFile(artifact) as archive:
        names = [name for name in archive.namelist() if name.endswith(".class")]
    assert len(names) == 176 and sorted(names) == sorted(proof["exactPermittedPhysicalNames"])
    return artifact


def main(output, mode):
    output = output.resolve()
    output.mkdir()
    head = H["git"]("rev-parse", "HEAD").decode().strip()
    tool = H["TOOL"]
    assert tool.read_bytes() == H["git"]("show", f"{head}:{tool}")
    java = H["JAVA"]
    libraries = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    fixture_mode = mode != "protocol"
    artifact = None if fixture_mode else protocol_input()
    steps = {}
    prior = set()
    expected = {
        (rule, PREFIX + owner, IMAGE_PREFIX + target)
        for owner, constructors, rule, deny in CASES if deny
        for target, _ in constructors
    }
    with TemporaryDirectory(prefix="pgpt-image-stream-audit-") as place:
        scratch = Path(place)
        source = scratch / tool.name
        source.write_bytes(tool.read_bytes())
        fixture_sources = []
        if fixture_mode:
            fixture_sources.extend(
                C["write_fixture"](scratch, PREFIX + owner, body(constructors))
                for owner, constructors, _, _ in CASES
            )
        earlier = earlier_sources(scratch, prior) if mode == "regression" else []
        fixture_sources.extend(earlier)
        fixture_sources.extend(
            C["write_fixture"](scratch, PREFIX + module + ".Anchor", C["MARKER"])
            for module in H["MODULES"] if fixture_mode or module != "protocol"
        )
        javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        for step, command in (
            ("compile-tool", [*javac, "-cp", libraries, "-d", scratch / "audit", source]),
            ("compile-fixtures", [*javac, "-d", scratch / "classes", *fixture_sources]),
        ):
            steps[step], _ = H["execute"](output, step, command, scratch)
            assert steps[step]["actualExit"] == 0
        owners, physical = ARCHIVE["prior"]["fixture_owners"](scratch / "classes")
        jars = {}
        for module, entries in owners.items():
            if artifact and module == "protocol":
                assert not entries
                jars[module] = artifact
                continue
            jar = scratch / (module + ".jar")
            H["archive"](jar, entries, scratch / "classes")
            jars[module] = jar
        if artifact:
            assert len(physical) == 5 and jars["protocol"] == artifact
        steps["audit"], _ = H["execute"](
            output, "audit",
            [java, "-cp", f"{scratch / 'audit'}{os.pathsep}{libraries}", "ModuleDependencyAudit",
             *(f"{module}={jar}" for module, jar in sorted(jars.items()))],
            scratch,
        )
    findings = SUPPORT["published_findings"](output / "audit.stdout.txt")
    assert findings == (expected | prior if mode == "regression" else set()), findings
    assert steps["audit"]["actualExit"] == int(mode == "regression")
    rows = [
        dict(
            testId=f"PT-F02-FILECALL{index:03}",
            fixture=PREFIX + owner,
            rule=rule,
            expectedTargets=sorted(IMAGE_PREFIX + name for name, _ in constructors) if deny else [],
            observedTargets=sorted(target for _, fixture, target in findings if fixture == PREFIX + owner),
        )
        for index, (owner, constructors, rule, deny) in enumerate(CASES, 18)
    ] if fixture_mode else []
    H["dump"](output / "manifest.json", dict(
        mode=mode, source=head, terminalAtUTC=datetime.now(timezone.utc).isoformat(), actualExit=0,
        cases=rows, missingFindings=len(expected - findings) if fixture_mode else 0,
        earlierSyntheticCases=len(earlier), earlierFindings=len(prior), observedTotal=len(findings),
        inspectedSyntheticClasses=len(physical), protocolClasses=176 if artifact else 0,
        pinnedInputs=[H["pin"](H[key]) for key in ("ARCH", "SLF", "JAVA", "TOOL")]
        + ([H["pin"](artifact)] if artifact else []),
        steps=steps, productTestRuns=0, imageOrFileActions=0,
    ))
    print(mode, len(rows), len(earlier), len(findings), len(physical))


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("output", type=Path)
    arguments.add_argument("mode", choices=("baseline", "regression", "protocol"))
    options = arguments.parse_args()
    main(options.output, options.mode)
