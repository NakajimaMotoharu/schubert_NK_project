"""Tool-only recurrence checks for six observed metadata label errors."""
import unittest

from pmo_group_context import build_context, validate_context


class GroupContextTest(unittest.TestCase):
    def fields(self, **changes):
        values = dict(group_id="PGPT-CURRENT-20261107", category="REVIEW",
                      kind="TOOL_FIX", scope="Explicit current metadata review",
                      oracle_refs=[dict(path="documents/400_PGPT/plan.md", sha256="a" * 64)])
        values.update(changes)
        return build_context(**values)

    def test_derived_identity_and_reused_context_rejected(self):
        fields = self.fields()
        self.assertEqual("PGPT-CURRENT-20261107", fields["workDetailCategory"])
        self.assertNotIn("groupId", fields)
        validate_context("PGPT-CURRENT-20261107", fields)
        with self.assertRaises(ValueError):
            validate_context("PGPT-OTHER-20261107", fields)
        fields["workDetailCategory"] = "YKT2152_WEB_OUTER_LIFECYCLE_STATIC_REVIEW"
        with self.assertRaises(ValueError):
            validate_context("PGPT-CURRENT-20261107", fields)

    def test_explicit_required_values(self):
        with self.assertRaises(TypeError):
            build_context(group_id="PGPT-CURRENT")
        for value in ([], None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.fields(oracle_refs=value)

    def test_unsafe_and_held_reference_names(self):
        for path in ("/documents/x.md", "documents/../x.md", "documents//x.md",
                     "documents\\x.md", "tools/a.json", "evidence/a.jar",
                     "evidence/private/a.json", "evidence/RootFailedStartRecoveryTest.md",
                     "evidence/SnapshotKeyCloseWitness.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.fields(oracle_refs=[dict(path=path, sha256="a" * 64)])

    def test_invalid_activity_fields(self):
        for change in (dict(group_id="PGPT-x"), dict(category="TOOL_FIX"),
                       dict(kind="UNKNOWN_COST_GUESSED"), dict(scope=" "),
                       dict(scope=None), dict(scope="x" * 4097)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.fields(**change)

    def test_exact_hash_and_source(self):
        for change in (dict(sha256="A" * 64), dict(sha256="a" * 63),
                       dict(sha256=None), dict(source=None), dict(source="b" * 39),
                       dict(extra="copied")):
            ref = dict(path="documents/p.md", sha256="a" * 64)
            ref.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.fields(oracle_refs=[ref])

    def test_duplicates_and_explicit_historical_versions(self):
        ref = dict(path="evidence/p.json", sha256="a" * 64, source="b" * 40)
        with self.assertRaises(ValueError):
            self.fields(oracle_refs=[ref, dict(ref, sha256="c" * 64)])
        result = self.fields(oracle_refs=[ref, dict(ref, source="c" * 40)])
        self.assertEqual(2, len(result["oracleReferences"]))

    def test_inputs_are_not_mutated_or_aliased(self):
        refs = [dict(path="documents/p.md", sha256="a" * 64)]
        result = self.fields(oracle_refs=refs)
        result["oracleReferences"][0]["sha256"] = "b" * 64
        self.assertEqual("a" * 64, refs[0]["sha256"])


if __name__ == "__main__":
    unittest.main()
