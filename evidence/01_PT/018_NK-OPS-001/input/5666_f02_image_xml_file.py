"""Statically check JDK direct File overloads against independent SS311 cases."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


FILELOG = runpy.run_path(str(Path(__file__).with_name("5648_f02_file_handler_contract.py")))
H, C, R, SUPPORT, ARCHIVE = (FILELOG[name] for name in ("H", "C", "R", "SUPPORT", "ARCHIVE"))
P, CONTROLLER, FENCE = H["P"], FILELOG["CONTROLLER"], FILELOG["FENCE"]
IMG = "javax.imageio.ImageIO"
DOM = "javax.xml.parsers.DocumentBuilder"
READ_FILE = "public Object read(java.io.File input) throws java.io.IOException { return javax.imageio.ImageIO.read(input); }"
WRITE_FILE = (
    "public boolean write(java.awt.image.RenderedImage image, java.io.File output) throws java.io.IOException "
    '{ return javax.imageio.ImageIO.write(image, "png", output); }'
)
PARSE_FILE = (
    "public Object parse(javax.xml.parsers.DocumentBuilder builder, java.io.File input) "
    "throws java.io.IOException, org.xml.sax.SAXException { return builder.parse(input); }"
)
READ_STREAM = (
    "public Object read(java.io.InputStream stream) throws java.io.IOException { return javax.imageio.ImageIO.read(stream); }"
)
PARSE_STREAM = (
    "public Object parse(javax.xml.parsers.DocumentBuilder builder, java.io.InputStream stream) "
    "throws java.io.IOException, org.xml.sax.SAXException { return builder.parse(stream); }"
)
CASES = (
    ("web.synthetic.ImageFileController", IMG, READ_FILE, CONTROLLER, True),
    ("web.synthetic.ImageWriteController", IMG, WRITE_FILE, CONTROLLER, True),
    ("web.synthetic.XmlFileController", DOM, PARSE_FILE, CONTROLLER, True),
    ("protocol.ImageFileSource", IMG, READ_FILE, FENCE, True),
    ("protocol.ImageFileSink", IMG, WRITE_FILE, FENCE, True),
    ("protocol.XmlFileSource", DOM, PARSE_FILE, FENCE, True),
    ("web.synthetic.ImageBorrowedController", IMG, READ_STREAM, CONTROLLER, False),
    ("protocol.XmlBorrowedStream", DOM, PARSE_STREAM, FENCE, False),
    ("web.synthetic.ImageOwnerAdapter", IMG, READ_FILE, CONTROLLER, False),
    ("batch.XmlOwnerAdapter", DOM, PARSE_FILE, FENCE, False),
)


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    context, = H["PLAN"].glob("1752_*.json")
    ctx = R["read"](context)["values"]
    tool = H["TOOL"]
    head = git("rev-parse", "HEAD").decode().strip()
    original = git("show", f'{ctx["source"]}:{tool}')
    assert H["sha"](original) == ctx["oracleReferences"][-1]["sha256"]
    current = git("show", f"{head}:{tool}")
    assert (current != original) == after
    assert not git("diff", "--name-only", ctx["source"], head, "--", "src")
    run = "PG41380-f02-image-xml-file-green-v1" if after else ctx["run"]
    out = H["OPS"] / run
    out.mkdir()
    steps = {}
    prior = set()
    wanted = {(r, P + owner, target) for owner, target, _, r, deny in CASES if deny}
    libs = os.pathsep.join(str(H[k]) for k in ("ARCH", "SLF"))
    java = H["JAVA"]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-image-xml-audit-") as place:
        root = Path(place)
        audit_source = root / tool.name
        audit_source.write_bytes(current)
        make = C["write_fixture"]
        sources = [make(root, P + owner, code) for owner, _, code, _, _ in CASES]
        if after:
            sources.extend(FILELOG["cases"](root, FILELOG["CASES"], prior))
            sources.extend(FILELOG["known"](root, prior))
        old_count = len(sources) - len(CASES)
        sources.extend(make(root, P + module + ".Anchor", C["MARKER"]) for module in H["MODULES"])
        javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        for step, command in (
            ("compile-tool", [*javac, "-cp", libs, "-d", root / "audit", audit_source]),
            ("compile-synthetic", [*javac, "-d", root / "classes", *sources]),
        ):
            steps[step], _ = execute(out, step, command, root)
            assert steps[step]["actualExit"] == 0
        owners, physical = ARCHIVE["prior"]["fixture_owners"](root / "classes")
        args = []
        for module, entries in sorted(owners.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, entries, root / "classes")
            args.append(f"{module}={jar}")
        steps["audit"], _ = execute(out, "audit", [java, "-cp", str(root / "audit") + os.pathsep + libs,
                                                  "ModuleDependencyAudit", *args], root)
    matched = SUPPORT["published_findings"](out / "audit.stdout.txt")
    assert matched == (wanted | prior if after else set())
    assert steps["audit"]["actualExit"] == int(after)
    rendered = [dict(testId=f"PT-F02-FILECALL{i:03}", syntheticClass=P+owner, target=target, rule=rule,
                     expected=deny, observed=(rule, P+owner, target) in matched)
                for i, (owner, target, _, rule, deny) in enumerate(CASES, 1)]
    H["dump"](out / "manifest.json", dict(
        run=run, actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=head,
        productionCore=ctx["productionCoreMain"], difference=H["sha"](current), testCases=rendered,
        misses=sum(row["expected"] != row["observed"] for row in rendered), priorSyntheticStaticCases=old_count,
        priorExpectedFindings=len(prior), physicalClasses=len(physical), originalActualAuditExit=steps["audit"]["actualExit"],
        productionTestRuns=0, syntheticInitializations=0, actualImageOrXmlCalls=0, actualExternalOperations=0,
        whole451=False, wholeF02=False, formalDelta=0, steps=steps))
    print(run, len(rendered), len(matched))


if __name__ == "__main__":
    main(sys.argv[1] == "green")
