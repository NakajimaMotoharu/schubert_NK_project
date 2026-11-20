"""Use the existing comparator harness with the two new Current dispositions."""

from pathlib import Path
import runpy
import sys


def main():
    mode = sys.argv[1]
    harness = runpy.run_path(str(Path(__file__).with_name("061_compare_definition_contract.py")))
    original = harness["main"]
    new_methods = (
        "rejectsCurrentRunCaseReportedAsNkOnly",
        "rejectsNkOnlyCaseReportedAsCurrentRun",
    )
    prior_methods = original.__globals__["TARGETS"]
    if mode == "red":
        original.__globals__["TARGETS"] = new_methods
        original("PG41334-p020-current-role-baseline-v1", "red")
    elif mode == "qualified":
        original.__globals__["TARGETS"] = prior_methods + new_methods
        original("PG41336-p020-current-role-qualified-v1", "qualified")
    else:
        raise SystemExit("Choose red or qualified")


if __name__ == "__main__":
    main()
