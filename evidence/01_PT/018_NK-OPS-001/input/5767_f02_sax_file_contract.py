"""Compile and audit synthetic direct SAX calls under SS311; do not execute fixtures."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory


IMAGE = runpy.run_path(str(Path(__file__).with_name("5666_f02_image_xml_file.py")))
H, C, SUPPORT, ARCHIVE, FILELOG = (
    IMAGE[name] for name in ("H", "C", "SUPPORT", "ARCHIVE", "FILELOG")
)
PREFIX, CONTROLLER, FENCE = (IMAGE[name] for name in ("P", "CONTROLLER", "FENCE"))
SAX = "javax.xml.parsers.SAXParser"
CASES = (
    ("web.synthetic.SaxFileController", "java.io.File", CONTROLLER, True),
    ("api.messaging.inbound.SaxFileListener", "java.io.File", FENCE, True),
    ("protocol.SaxFileSource", "java.io.File", FENCE, True),
    ("web.synthetic.SaxStreamController", "java.io.InputStream", CONTROLLER, False),
    ("api.messaging.inbound.SaxStreamListener", "java.io.InputStream", FENCE, False),
    ("protocol.SaxStreamSource", "java.io.InputStream", FENCE, False),
    ("batch.SaxFileAdapter", "java.io.File", FENCE, False),
)


def main(output, regression):
    output = output.resolve()
    output.mkdir()
    source_at = H["git"]("rev-parse", "HEAD").decode().strip()
    java = H["JAVA"]
    tool = H["TOOL"]
    tool_bytes = H["git"]("show", f"{source_at}:{tool}")
    assert tool.read_bytes() == tool_bytes
    libraries = os.pathsep.join(str(H[name]) for name in ("ARCH", "SLF"))
    write = C["write_fixture"]
    steps, prior = {}, set()
    expected = {(r, PREFIX + owner, SAX) for owner, _kind, r, deny in CASES if deny}
    with TemporaryDirectory(prefix="pgpt-sax-file-") as place:
        scratch = Path(place)
        fixtures = [
            write(
                scratch,
                PREFIX + owner,
                f"public void run({SAX} parser, {kind} input, org.xml.sax.helpers.DefaultHandler handler)"
                " throws java.io.IOException, org.xml.sax.SAXException { parser.parse(input, handler); }",
            )
            for owner, kind, _, _ in CASES
        ]
        if regression:
            fixtures.extend(
                write(scratch, PREFIX + owner, body)
                for owner, _kind, body, _rule, _deny in IMAGE["CASES"]
            )
            prior.update(
                (rule, PREFIX + owner, target)
                for owner, target, _body, rule, deny in IMAGE["CASES"]
                if deny
            )
            fixtures.extend(FILELOG["cases"](scratch, FILELOG["CASES"], prior))
            fixtures.extend(FILELOG["known"](scratch, prior))
        prior_count = len(fixtures) - len(CASES)
        fixtures.extend(
            write(scratch, PREFIX + module + ".Anchor", C["MARKER"]) for module in H["MODULES"]
        )
        auditor = scratch / tool.name
        auditor.write_bytes(tool_bytes)
        javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        for step, command in (
            ("jdk-overloads", [java.with_name("javap"), SAX]),
            ("compile-tool", [*javac, "-cp", libraries, "-d", scratch / "audit", auditor]),
            ("compile-fixtures", [*javac, "-d", scratch / "classes", *fixtures]),
        ):
            steps[step], _ = H["execute"](output, step, command, scratch)
            assert steps[step]["actualExit"] == 0
        signatures = (output / "jdk-overloads.stdout.txt").read_text().splitlines()
        assert sum("parse(java.io.File," in line for line in signatures) == 2
        assert sum("parse(java.io.InputStream," in line for line in signatures) == 4
        owners, physical = ARCHIVE["prior"]["fixture_owners"](scratch / "classes")
        args = []
        for module, entries in sorted(owners.items()):
            jar = scratch / (module + ".jar")
            H["archive"](jar, entries, scratch / "classes")
            args.append(f"{module}={jar}")
        steps["audit"], _ = H["execute"](
            output,
            "audit",
            [java, "-cp", str(scratch / "audit") + os.pathsep + libraries, "ModuleDependencyAudit", *args],
            scratch,
        )
    observed = SUPPORT["published_findings"](output / "audit.stdout.txt")
    assert observed == (expected | prior if regression else set())
    assert steps["audit"]["actualExit"] == int(regression)
    case_rows = [
        dict(
            testId=f"PT-F02-FILECALL{index:03}",
            fixture=PREFIX + owner,
            argument=kind,
            rule=rule,
            expected=deny,
            observed=(rule, PREFIX + owner, SAX) in observed,
        )
        for index, (owner, kind, rule, deny) in enumerate(CASES, 11)
    ]
    H["dump"](
        output / "manifest.json",
        dict(
            run=output.name,
            source=source_at,
            terminalAtUTC=datetime.now(timezone.utc).isoformat(),
            actualExit=0,
            syntheticFindings=case_rows,
            missingExpected=len(expected - observed),
            priorSyntheticCases=prior_count,
            priorExpectedFindings=len(prior),
            observedTotal=len(observed),
            inspectedSyntheticClasses=len(physical),
            pinnedInputs=[H["pin"](H[name]) for name in ("ARCH", "SLF", "JAVA", "TOOL")],
            steps=steps,
            realProductOrXmlOrFileActions=0,
        ),
    )
    print(output.name, len(CASES), prior_count, len(observed))


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("output", type=Path)
    arguments.add_argument("--regression", action="store_true")
    options = arguments.parse_args()
    main(options.output, options.regression)
