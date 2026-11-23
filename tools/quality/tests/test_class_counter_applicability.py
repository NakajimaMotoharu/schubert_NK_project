"""Verify measured-class qualification against synthetic and published counters."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import unittest

from class_counter_applicability import classify


EVIDENCE = Path(__file__).resolve().parents[3] / "evidence/01_PT"


def count(counters, expected_digest):
    content = counters.read_bytes()
    if sha256(content).hexdigest() != expected_digest:
        raise ValueError("fixed counter input changed")
    rows = json.loads(content)["physicalClasses"]
    return Counter(classify(row["counters"]) for row in rows.values())


def measured_class():
    return {
        "LINE": {"missed": 0, "covered": 5},
        "METHOD": {"missed": 0, "covered": 2},
        "CLASS": {"missed": 0, "covered": 1},
        "BRANCH": {"missed": 0, "covered": 0},
    }


class ClassCounterApplicabilityTest(unittest.TestCase):
    def test_executable_branchless_class(self):
        self.assertEqual("FOUR100_MEASURED_APPLICABLE", classify(measured_class()))

    def test_covered_branches(self):
        counters = measured_class()
        counters["BRANCH"]["covered"] = 2
        self.assertEqual("FOUR100_MEASURED_APPLICABLE", classify(counters))

    def test_missed_branch_is_not_a_pass(self):
        counters = measured_class()
        counters["BRANCH"] = {"missed": 1, "covered": 1}
        self.assertEqual("MISSED_COUNTERS", classify(counters))

    def test_missing_class_counter_is_incomplete(self):
        counters = measured_class()
        counters["CLASS"]["covered"] = 0
        self.assertEqual("INCOMPLETE_APPLICABILITY_NOT_A_MEASURED_PASS", classify(counters))

    def test_all_zero_is_not_a_measured_pass(self):
        counters = measured_class()
        for value in counters.values():
            value["covered"] = 0
        self.assertEqual("NO_COUNTERS_NOT_A_MEASURED_PASS", classify(counters))

    def test_aggregate_cannot_be_used_for_one_physical_class(self):
        for missed, covered in ((0, 2), (1, 1), (2, 0)):
            with self.subTest(missed=missed, covered=covered):
                counters = measured_class()
                counters["CLASS"] = {"missed": missed, "covered": covered}
                with self.assertRaisesRegex(ValueError, "at most one physical class"):
                    classify(counters)

    def test_invalid_scalar_counts(self):
        for value in (True, -1, 1.0, None):
            with self.subTest(value=value):
                counters = measured_class()
                counters["CLASS"]["covered"] = value
                with self.assertRaisesRegex(ValueError, "nonnegative integer counters"):
                    classify(counters)

    def test_published_protocol_counter_examples_keep_their_classification(self):
        expected_whole = {"FOUR100_MEASURED_APPLICABLE": 159, "NO_COUNTERS_NOT_A_MEASURED_PASS": 10}
        whole_digest = "7d88a2dad8af07a7b84bd3b0a4e1dd1a1756fcb1fa1670d135f7734990daa4e8"
        previous = EVIDENCE / "002_NK-PRO-002/evidence/provisional"
        cross_reference = EVIDENCE / "018_NK-OPS-001/evidence/provisional"
        examples = (
            (previous / "PG9724-protocol-module-post-v2/whole-module-counters.json",
             whole_digest, expected_whole),
            (cross_reference / "PG10190-protocol-module-post-v1/whole-module-counters.json",
             whole_digest, expected_whole),
            (previous / "PG9716-typed-boundaries-component-post-v1/source-unit-counters.json",
             "a5a957e50a98556e399d37caa93eeba8ebf80846023b1fee045ed94437541902",
             {"FOUR100_MEASURED_APPLICABLE": 75}),
        )
        for path, digest, expected in examples:
            with self.subTest(path=path.parent.name):
                self.assertEqual(expected, count(path, digest))
