"""Run caller-provided normal metadata vectors for the explicit class-name check."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from io import StringIO
import json
import sys
import unittest


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


phase = sys.argv[1]
assert phase in ("before", "after", "after-compatibility")
sys.path.insert(0, str(Path("tools/quality").resolve()))
suite_base = "jacoco_readonly_exec_subset"
suffixes = ("encoding_test", "modified_utf_test", "presence_test", "scope_test", "test")
modules = [f"{suite_base}_{s}" for s in suffixes]
test = modules[-2] + ".ClassSelectionScopeTest.test_empty_class_name_is_invalid_even_with_a_known_target"
names = [test] if phase == "before" else modules
out = (Path("evidence/01_PT/018_NK-OPS-001/evidence") /
       {"before": "PG40896-offline-class-selector-empty-name-v1-before",
        "after": "PG40898-offline-class-selector-empty-name-v1-after",
        "after-compatibility": "PG40900-offline-class-selector-legacy-message-v1"}[phase])
out.mkdir()
start = datetime.now(timezone.utc).isoformat()
stream = StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestLoader().loadTestsFromNames(names))
text = stream.getvalue()
exit_code = 0 if result.wasSuccessful() else 1
if phase == "before":
    matched = (exit_code == 1 and result.testsRun == 1 and len(result.failures) == 2 and
               not result.errors and "one session and all exact target records required" in text)
else:
    matched = exit_code == 0 and result.testsRun == 32 and not result.skipped
(out / "result.txt").write_text(text)
data = dict(actualExit=exit_code, expectedMatched=matched, phase=phase, startedAtUTC=start,
            terminalAtUTC=datetime.now(timezone.utc).isoformat(), pythonVersion=sys.version.split()[0],
            toolPin=pin(Path("tools/quality/jacoco_readonly_exec_subset.py")),
            fixturePins=[pin(Path("tools/quality") / (n + ".py")) for n in modules],
            selected=names, tests=result.testsRun, failures=len(result.failures),
            errors=len(result.errors), skipped=len(result.skipped), result=pin(out / "result.txt"),
            newToolCase="PT-NATIVE-META-SELECT005", actualNativeActions=0, actualProductTests=0,
            actualArtifactStreamReads=0, newFormalAcceptance=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), exit_code, result.testsRun, matched)
raise SystemExit(0 if matched else 1)
