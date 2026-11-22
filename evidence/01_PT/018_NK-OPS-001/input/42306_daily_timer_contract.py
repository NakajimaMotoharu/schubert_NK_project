"""Read the scheduled maintenance timer and check its offline calendar semantics."""

import configparser
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


CALENDAR_CASES = (
    (
        "2026-11-21 19:59:59 UTC",
        ("2026-11-21 20:00:00 UTC", "2026-11-22 20:00:00 UTC"),
    ),
    (
        "2026-11-21 20:00:00 UTC",
        ("2026-11-22 20:00:00 UTC", "2026-11-23 20:00:00 UTC"),
    ),
    (
        "2026-11-21 20:00:01 UTC",
        ("2026-11-22 20:00:00 UTC", "2026-11-23 20:00:00 UTC"),
    ),
    (
        "2026-12-30 20:00:01 UTC",
        ("2026-12-31 20:00:00 UTC", "2027-01-01 20:00:00 UTC"),
    ),
)


def check_timer(template: Path, parser: str) -> dict:
    unit = configparser.ConfigParser(delimiters=("=",), interpolation=None, strict=True)
    unit.optionxform = str
    with template.open(encoding="utf-8") as stream:
        unit.read_file(stream)
    assert unit.sections() == ["Unit", "Timer", "Install"]
    assert set(unit["Unit"]) == {"Description"}
    assert dict(unit["Timer"]) == {
        "OnCalendar": "*-*-* 05:00:00 Asia/Tokyo",
        "Persistent": "false",
        "Unit": "schubert-nk-maintenance.service",
    }
    assert dict(unit["Install"]) == {"WantedBy": "timers.target"}

    env = dict(os.environ, LC_ALL="C", TZ="UTC")
    observations = []
    for base, expected in CALENDAR_CASES:
        result = subprocess.run(
            [parser, "calendar", "--iterations=2", f"--base-time={base}", unit["Timer"]["OnCalendar"]],
            capture_output=True,
            check=True,
            env=env,
            text=True,
            timeout=10,
        )
        actual = tuple(
            re.findall(
                r"^\s*(?:Next elapse|Iteration #2): \w{3} ([-\d :]+ UTC)$",
                result.stdout,
                re.MULTILINE,
            )
        )
        assert actual == expected, (base, expected, actual)
        observations.append({"baseUTC": base, "expectedUTC": expected, "observedUTC": actual})

    return {
        "PT-OPS-MAINT-PREBOOT001-T01": "PASS",
        "PT-OPS-MAINT-PREBOOT001-T02": {"status": "PASS", "cases": observations},
    }


def check_invalid_entries(template: Path) -> list[str]:
    contents = template.read_text(encoding="utf-8")
    inputs = {
        "duplicateCalendar": contents.replace("[Install]", "OnCalendar=05:00\n\n[Install]"),
        "wrongService": contents.replace("schubert-nk-maintenance.service", "fixture.service"),
        "missedTimerReplay": contents.replace("Persistent=false", "Persistent=true"),
        "wrongTimeZone": contents.replace("Asia/Tokyo", "UTC"),
    }
    rejected = []
    with tempfile.TemporaryDirectory(prefix="nk-timer-fixture-") as directory:
        for name, text in inputs.items():
            assert text != contents
            fixture = Path(directory) / f"{name}.timer"
            fixture.write_text(text, encoding="utf-8")
            try:
                check_timer(fixture, str(Path(directory) / "unavailable-calendar-parser"))
            except (AssertionError, configparser.DuplicateOptionError):
                rejected.append(name)
            else:
                raise AssertionError(f"accepted an invalid timer fixture: {name}")
    return rejected


if __name__ == "__main__":
    template = Path(sys.argv[1])
    evidence = check_timer(template, sys.argv[2])
    evidence["rejectedSyntheticInputs"] = check_invalid_entries(template)
    print(json.dumps(evidence, indent=2))
