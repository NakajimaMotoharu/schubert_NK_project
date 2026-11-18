"""Independent local sibling-file and compressed-archive contract for BUG-3265."""
import gzip
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory

tool = Path(__file__).with_name("5129_f03_current_source_lint_join.py")
module = spec_from_file_location("stage_stream_join", tool)
current = module_from_spec(module)
module.loader.exec_module(current)
root = Path("evidence/01_PT/018_NK-OPS-001/evidence/PG39306-f03-current-source-lint-join-v1")
expected = {"stdoutSha256": hashlib.sha256(b"A\r\n").hexdigest(),
            "stderrSha256": hashlib.sha256(b"B\n").hexdigest()}
with TemporaryDirectory(prefix="pg39308-stage-stream-") as fixture:
    f = Path(fixture)
    (f / "checkstyle.stdout").write_bytes(b"A\r\n")
    (f / "checkstyle.stderr").write_bytes(b"B\n")
    assert current.verify_stream(f / "checkstyle", expected)
    (f / "format.stdout.gz").write_bytes(gzip.compress(b"A\r\n", mtime=0))
    (f / "format.stderr").write_bytes(b"B\n")
    assert current.verify_stream(f / "format", expected)
    (f / "format.stderr").write_bytes(b"incorrect\n")
    assert not current.verify_stream(f / "format", expected)
    assert not current.verify_stream(f / "absent", expected)
    (f / "format.stdout.gz").write_bytes(b"incorrect archive")
    assert not current.verify_stream(f / "format", expected)
with (root / "stream-fixture.json").open("x") as output:
    json.dump(dict(actualExit=0, plainExpected=True, archiveExpected=True,
                   mutationRejected=True, missingRejected=True, brokenArchiveRejected=True,
                   productTestCount=0, related=["BUG-3265","YKT-2692"]), output, indent=2)
    output.write("\n")
