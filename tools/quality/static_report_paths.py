"""Check the report paths of a local static-analysis plan before starting its tools."""

import argparse
import json
from pathlib import Path

from static_input_scope import ScopeError, read_metadata


REPORT_OPTIONS = {
    "checkstyle": ("-o", "--output"),
    "pmd": ("-r", "--report-file"),
    "spotbugs": ("-output",),
}


def option_value(argv: list[str], options: tuple[str, ...]) -> str:
    matches = []
    for index, arg in enumerate(argv):
        option, separator, embedded = arg.partition("=")
        if option in options:
            value = embedded
            if not separator and index + 1 < len(argv):
                value = argv[index + 1]
            matches.append(value)
    if len(matches) != 1 or not matches[0]:
        raise ScopeError("MISSING_OR_AMBIGUOUS_PATH_OPTION")
    return matches[0]


def verify_report_paths(directory: Path, stages: dict) -> dict[str, str]:
    """Check direct, unused report paths under an already owned run directory."""
    if not directory.is_absolute() or directory.resolve(strict=True) != directory:
        raise ScopeError("RUN_DIRECTORY_NOT_CANONICAL")
    if not directory.is_dir():
        raise ScopeError("RUN_DIRECTORY_NOT_DIRECTORY")
    if not isinstance(stages, dict) or not stages or stages.keys() - REPORT_OPTIONS.keys():
        raise ScopeError("INVALID_STATIC_STAGE_SET")

    outputs = {}
    for name, argv in stages.items():
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) for arg in argv):
            raise ScopeError("INVALID_STATIC_ARGUMENTS")
        expected = directory / f"{name}.xml"
        actual = Path(option_value(argv, REPORT_OPTIONS[name]))
        if actual != expected:
            raise ScopeError("REPORT_OUTSIDE_CURRENT_RUN")
        if expected.is_symlink() or expected.exists():
            raise ScopeError("REPORT_PATH_ALREADY_USED")
        if name == "pmd":
            sources = directory / "sources.txt"
            if Path(option_value(argv, ("--file-list",))) != sources:
                raise ScopeError("FILE_LIST_OUTSIDE_CURRENT_RUN")
            if sources.is_symlink() or not sources.is_file():
                raise ScopeError("FILE_LIST_NOT_LOCAL_FILE")
        outputs[name] = str(expected)
    return outputs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        outputs = verify_report_paths(args.run_directory, read_metadata(args.plan).get("stages"))
    except ScopeError as error:
        print(json.dumps({"reportPathsMatch": False, "reason": str(error)}))
        return 1
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"reportPathsMatch": False, "reason": "UNREADABLE_RUN_OR_PLAN"}))
        return 1
    print(json.dumps({"reportPathsMatch": True, "reports": outputs}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
