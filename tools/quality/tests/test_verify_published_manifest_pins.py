import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from verify_published_manifest_pins import audit


FIXTURE = "src/example.txt"
MANIFEST = "evidence/01_PT/001_fixture/evidence/manifest.json"
INITIAL = b"independent original sample\n"
UPDATED = b"independent revised sample\n"


def pin(path, expected, **fields):
    return {"path": str(path), "sha256": hashlib.sha256(expected).hexdigest(), **fields}


class PublishedManifestPinsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.git("init", "-q")
        self.write(FIXTURE, INITIAL)
        self.original = self.commit()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
            cwd=self.repo,
            stderr=subprocess.PIPE,
            text=True,
        ).strip()

    def write(self, name, content):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def manifest(self, value, name=MANIFEST):
        self.write(name, json.dumps(value).encode())

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture revision")
        return self.git("rev-parse", "HEAD")

    def test_exact_source_can_precede_the_current_range(self):
        self.write(FIXTURE, UPDATED)
        start = self.commit()
        self.manifest(
            {
                "inputs": [
                    pin(FIXTURE, INITIAL, source=self.original),
                    pin(self.repo / FIXTURE, UPDATED),
                    pin("../local-only.txt", b"external synthetic"),
                    pin("program/characterization/baseline/current/fixture.txt", INITIAL),
                ]
            }
        )
        end = self.commit()

        result = audit(self.repo, start, end)

        self.assertEqual(1, result["manifests"])
        self.assertEqual(1, result["current"])
        self.assertEqual(1, result["historical"])
        self.assertEqual(2, result["externalOrProtected"])
        self.assertEqual([], result["unresolved"])

    def test_named_source_requires_its_own_hash(self):
        self.write(FIXTURE, UPDATED)
        self.manifest({"nested": pin(FIXTURE, UPDATED, source=self.original)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual(0, result["current"])
        self.assertEqual(
            [{"manifest": MANIFEST, **pin(FIXTURE, UPDATED, source=self.original)}],
            result["unresolved"],
        )

    def test_explicit_source_must_name_a_full_commit_without_implicit_fallback(self):
        for invalid in (self.original[:9], "HEAD", None, 123):
            with self.subTest(invalid=invalid):
                # Each digest matches the latest bytes. The explicit source still must bind them.
                self.manifest({"reference": pin(FIXTURE, INITIAL, source=invalid)})
                end = self.commit()

                result = audit(self.repo, self.original, end)

                self.assertEqual(0, result["current"])
                self.assertEqual(
                    [
                        {
                            "manifest": MANIFEST,
                            **pin(FIXTURE, INITIAL, source=None),
                            "reason": "INVALID_EXPLICIT_SOURCE",
                        }
                    ],
                    result["unresolved"],
                )

    def test_tree_object_id_cannot_substitute_for_a_source_commit(self):
        tree = self.git("rev-parse", self.original + "^{tree}")
        self.manifest({"reference": pin(FIXTURE, INITIAL, source=tree)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual(0, result["historical"])
        self.assertEqual("INVALID_EXPLICIT_SOURCE", result["unresolved"][0]["reason"])

    def test_invalid_declared_digest_cannot_disappear_from_the_pin_count(self):
        for invalid in (None, "0" * 63, "z" * 64):
            with self.subTest(invalid=invalid):
                self.manifest(
                    {
                        "reference": {"path": FIXTURE, "sha256": invalid},
                        "observation": {"path": "src/observation.txt"},
                    }
                )
                end = self.commit()

                result = audit(self.repo, self.original, end)

                self.assertEqual(0, result["current"])
                self.assertEqual(
                    [
                        {
                            "manifest": MANIFEST,
                            "path": FIXTURE,
                            "sha256": None,
                            "source": None,
                            "reason": "INVALID_EXPLICIT_SHA256",
                        }
                    ],
                    result["unresolved"],
                )

    def test_malformed_declared_paths_are_not_counted_as_external_or_ignored(self):
        expected = hashlib.sha256(INITIAL).hexdigest()
        for malformed in (" ", None, 12, [], ""):
            self.manifest(
                {
                    "attempted": {"path": malformed, "sha256": expected},
                    "unobserved": {"path": None, "sha256": None},
                    "valid": pin(FIXTURE, INITIAL),
                    "external": pin("../public-fixture.txt", INITIAL),
                }
            )
            self.git("add", ".")
            head = self.git("rev-parse", "HEAD")
            staged = audit(self.repo, self.original, head, staged=True)
            end = self.commit()
            committed = audit(self.repo, self.original, end)

            for result in (staged, committed):
                with self.subTest(malformed=malformed, staged="stagedTree" in result):
                    self.assertEqual(1, result["current"])
                    self.assertEqual(1, result["externalOrProtected"])
                    self.assertEqual(
                        [
                            {
                                "manifest": MANIFEST,
                                "path": None,
                                "sha256": expected,
                                "source": None,
                                "reason": "INVALID_EXPLICIT_PATH",
                            }
                        ],
                        result["unresolved"],
                    )

    def test_unrepresentable_path_is_never_classified_as_external(self):
        expected = hashlib.sha256(INITIAL).hexdigest()
        for malformed in ("src/invalid\0name", "../invalid\0name"):
            self.manifest(
                {
                    "invalid": {"path": malformed, "sha256": expected},
                    "valid": pin(FIXTURE, INITIAL),
                    "external": pin("../public-fixture.txt", INITIAL),
                }
            )
            self.git("add", ".")
            head = self.git("rev-parse", "HEAD")
            staged = audit(self.repo, self.original, head, staged=True)
            end = self.commit()
            committed = audit(self.repo, self.original, end)

            for result in (staged, committed):
                with self.subTest(stage="stagedTree" in result, form=malformed.split("/")[0]):
                    self.assertEqual(1, result["current"])
                    self.assertEqual(1, result["externalOrProtected"])
                    self.assertEqual(
                        [
                            {
                                "manifest": MANIFEST,
                                "path": None,
                                "sha256": expected,
                                "source": None,
                                "reason": "INVALID_EXPLICIT_PATH",
                            }
                        ],
                        result["unresolved"],
                    )

    def test_current_tree_is_from_commit_and_never_from_worktree(self):
        self.manifest([pin(FIXTURE, INITIAL), pin(FIXTURE, INITIAL)])
        self.manifest([pin(FIXTURE, UPDATED)], "documents/manifest.json")
        end = self.commit()
        self.write(FIXTURE, UPDATED)

        result = audit(self.repo, self.original, end)

        self.assertEqual(1, result["manifests"])
        self.assertEqual(1, result["current"])
        self.assertEqual([], result["unresolved"])

    def test_manifest_type_change_is_reported_in_both_git_snapshots(self):
        self.manifest({"reference": pin(FIXTURE, INITIAL)})
        start = self.commit()
        manifest = self.repo / MANIFEST
        manifest.unlink()
        manifest.symlink_to("unused-fixture.json")
        self.git("add", MANIFEST)

        staged = audit(self.repo, start, start, staged=True)
        committed = audit(self.repo, start, self.commit())

        for result in (staged, committed):
            with self.subTest(staged="stagedTree" in result):
                self.assertEqual(1, result["manifests"])
                self.assertEqual(0, result["current"])
                self.assertEqual(
                    [{"manifest": MANIFEST, "reason": "NON_REGULAR_MANIFEST"}],
                    result["unresolved"],
                )

    def test_public_pin_requires_the_bytes_of_a_regular_git_file(self):
        linked = "src/linked.txt"
        target = Path(FIXTURE).name
        (self.repo / linked).symlink_to(target)
        reference = pin(linked, target.encode())
        self.manifest({"link": reference, "regular": pin(FIXTURE, INITIAL)})
        self.git("add", linked, MANIFEST)

        staged = audit(self.repo, self.original, self.original, staged=True)
        committed = audit(self.repo, self.original, self.commit())

        for result in (staged, committed):
            with self.subTest(staged="stagedTree" in result):
                self.assertEqual(1, result["current"])
                self.assertEqual(0, result["historical"])
                self.assertEqual(
                    [{"manifest": MANIFEST, **reference, "source": None}],
                    result["unresolved"],
                )

    def test_implicit_reference_uses_its_published_history(self):
        self.write(FIXTURE, UPDATED)
        self.commit()
        self.write(FIXTURE, b"third version\n")
        self.manifest({"reference": pin(FIXTURE, UPDATED)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual(1, result["historical"])
        self.assertEqual([], result["unresolved"])

    def test_staged_manifest_and_input_use_one_index_snapshot(self):
        self.write(FIXTURE, UPDATED)
        self.manifest({"reference": pin(FIXTURE, UPDATED)})
        self.git("add", FIXTURE, MANIFEST)
        self.write(FIXTURE, b"unstaged input\n")
        self.manifest({"reference": pin("src/unstaged.txt", INITIAL)})

        result = audit(self.repo, self.original, self.original, staged=True)

        self.assertEqual(self.original, result["rangeEnd"])
        self.assertEqual(self.git("write-tree"), result["stagedTree"])
        self.assertEqual(1, result["current"])
        self.assertEqual([], result["unresolved"])
        self.assertEqual(0, audit(self.repo, self.original, self.original)["manifests"])

    def test_staged_manifest_rejects_a_worktree_only_input_before_commit(self):
        local = "src/host-only-report.txt"
        self.write(local, UPDATED)
        self.manifest({"reference": pin(local, UPDATED)})
        self.git("add", MANIFEST)

        result = audit(self.repo, self.original, self.original, staged=True)

        self.assertEqual(0, result["current"])
        self.assertEqual(
            [{"manifest": MANIFEST, **pin(local, UPDATED, source=None)}],
            result["unresolved"],
        )

    def test_staged_tree_cannot_satisfy_an_explicit_commit_source(self):
        self.write(FIXTURE, UPDATED)
        self.manifest({"reference": pin(FIXTURE, UPDATED, source=self.original)})
        self.git("add", FIXTURE, MANIFEST)

        result = audit(self.repo, self.original, self.original, staged=True)

        self.assertEqual(0, result["current"])
        self.assertEqual(
            [{"manifest": MANIFEST, **pin(FIXTURE, UPDATED, source=self.original)}],
            result["unresolved"],
        )

    def test_missing_path_is_reported_and_invalid_commit_is_rejected(self):
        self.manifest({"reference": pin("src/absent.txt", INITIAL)})
        end = self.commit()

        result = audit(self.repo, self.original, end)

        self.assertEqual("src/absent.txt", result["unresolved"][0]["path"])
        with self.assertRaises(ValueError):
            audit(self.repo, "HEAD", end)

    def test_malformed_json_observations_are_rejected_before_counting_pins(self):
        cases = (
            ("duplicate field", b'{"observation": 1, "observation": 2}'),
            ("non-finite number", b'{"observation": NaN}'),
            ("negative infinity", b'{"observation": -Infinity}'),
        )
        for label, raw in cases:
            with self.subTest(label=label):
                self.write(MANIFEST, raw)
                end = self.commit()
                with self.assertRaises(ValueError):
                    audit(self.repo, self.original, end)


if __name__ == "__main__":
    unittest.main()
