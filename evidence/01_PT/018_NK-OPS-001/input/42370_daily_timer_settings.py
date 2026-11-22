"""Verify the explicit daily timer timing contract offline."""

import configparser
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def verify_unit(contents: str) -> None:
    unit = configparser.ConfigParser(delimiters=("=",), interpolation=None, strict=True)
    unit.optionxform = str
    unit.read_string(contents)
    assert unit.sections() == ["Unit", "Timer", "Install"]
    assert set(unit["Unit"]) == {"Description"}
    assert dict(unit["Timer"]) == {
        "OnCalendar": "*-*-* 05:00:00 Asia/Tokyo",
        "AccuracySec": "1min",
        "RandomizedDelaySec": "0",
        "Persistent": "false",
        "Unit": "schubert-nk-maintenance.service",
    }
    assert dict(unit["Install"]) == {"WantedBy": "timers.target"}


def main(template: Path, analyzer: str) -> None:
    contents = template.read_text(encoding="utf-8")
    verify_unit(contents)
    variants = {
        "missingAccuracy": ("AccuracySec=1min\n", ""),
        "wrongAccuracy": ("AccuracySec=1min", "AccuracySec=2min"),
        "duplicateAccuracy": ("AccuracySec=1min", "AccuracySec=1min\nAccuracySec=1min"),
        "missingDelay": ("RandomizedDelaySec=0\n", ""),
        "wrongDelay": ("RandomizedDelaySec=0", "RandomizedDelaySec=1min"),
        "duplicateDelay": ("RandomizedDelaySec=0", "RandomizedDelaySec=0\nRandomizedDelaySec=0"),
    }
    rejected = []
    for name, (literal, replacement) in variants.items():
        assert contents.count(literal) == 1
        try:
            verify_unit(contents.replace(literal, replacement))
        except (AssertionError, configparser.DuplicateOptionError):
            rejected.append(name)
        else:
            raise AssertionError(f"accepted invalid timing fixture: {name}")

    parsed = subprocess.run(
        [analyzer, "timespan", "1min", "0"],
        capture_output=True,
        check=True,
        env=dict(os.environ, LC_ALL="C.UTF-8", TZ="UTC"),
        encoding="utf-8",
        timeout=10,
    )
    durations = [int(value) for value in re.findall(r"^\s*μs: (\d+)$", parsed.stdout, re.MULTILINE)]
    assert durations == [60_000_000, 0]
    print(json.dumps({
        "testId": "PT-OPS-MAINT-PREBOOT001-T03",
        "status": "PASS",
        "timingMicroseconds": durations,
        "rejectedSyntheticInputs": rejected,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
