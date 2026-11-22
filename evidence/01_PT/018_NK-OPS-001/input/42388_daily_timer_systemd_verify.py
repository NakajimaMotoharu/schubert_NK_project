"""Verify the current timer offline with a deliberately non-functional service stub."""

import configparser
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def has_reference(timer: Path) -> bool:
    unit = configparser.ConfigParser(delimiters=("=",), interpolation=None, strict=True)
    unit.optionxform = str
    with timer.open(encoding="utf-8") as stream:
        unit.read_file(stream)
    reference = unit["Timer"]["Unit"]
    assert reference == "schubert-nk-maintenance.service"
    return timer.with_name(reference).is_file()


def main(source: Path, analyzer: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="nk-timer-verify-") as directory:
        units = Path(directory)
        timer = units / "schubert-nk-maintenance.timer"
        service = units / "schubert-nk-maintenance.service"
        for name in ("basic.target", "sysinit.target", "shutdown.target", "timers.target"):
            (units / name).write_text(
                "[Unit]\nDescription=Offline syntax fixture\nDefaultDependencies=no\n",
                encoding="utf-8",
            )
        service.write_text(
            "[Unit]\nDefaultDependencies=no\n[Service]\nType=oneshot\n"
            "ExecStart=/usr/bin/false\nStandardOutput=null\nStandardError=null\n",
            encoding="utf-8",
        )
        env = dict(os.environ, SYSTEMD_UNIT_PATH=directory, LC_ALL="C.UTF-8", TZ="UTC")
        command = [
            str(analyzer),
            "--generators=false",
            "--man=false",
            "--recursive-errors=yes",
            "verify",
            str(timer),
        ]
        original = source.read_bytes()
        timer.write_bytes(original)
        assert has_reference(timer)
        correct = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
        assert correct.returncode == 0 and not correct.stderr, correct.stderr

        assert original.count(b"AccuracySec=1min") == 1
        timer.write_bytes(original.replace(b"AccuracySec=1min", b"FixtureAccuracySec=1min"))
        invalid = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
        assert invalid.returncode != 0
        assert "FixtureAccuracySec" in invalid.stderr and "Unknown key" in invalid.stderr

        timer.write_bytes(original)
        service.unlink()
        missing = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30)
        assert not has_reference(timer)

    print(json.dumps({
        "testId": "PT-OPS-MAINT-PREBOOT001-T04",
        "validSyntaxExit": correct.returncode,
        "unknownKeyExit": invalid.returncode,
        "missingServiceNativeVerifyExit": missing.returncode,
        "missingServiceReferenceDetected": True,
        "syntheticDependency": True,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
