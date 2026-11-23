import hashlib
import unittest

from verify_protocol_fixture_provenance import UI_DOCUMENTS, verify_provenance


def sha256(value):
    return hashlib.sha256(value).hexdigest().encode("ascii")


class ProtocolFixtureProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.designs = dict(zip(UI_DOCUMENTS, (b"auth", b"media-and-log", b"management")))
        self.rows = [
            b"# source-sha256 " + path.encode("utf-8") + b"=" + sha256(body)
            for path, body in self.designs.items()
        ]

    def bad_links(self, fields, golden):
        checks = verify_provenance(fields, golden, self.designs)
        return [check.get("source") for check in checks if check["status"] != "match"]

    @staticmethod
    def golden(fields):
        return b"# fields-ui234-236.tsv-sha256=" + sha256(fields) + b"\n"

    def test_current_chain_matches(self):  # PT-OPS-ORIGIN-PRO001
        fields = b"\n".join(self.rows)
        self.assertEqual([], self.bad_links(fields, self.golden(fields)))

    def test_only_old_design_link_fails_with_correct_field_link(self):  # PT-OPS-ORIGIN-PRO002
        self.rows[1] = self.rows[1].split(b"=", 1)[0] + b"=" + sha256(b"prior media")
        fields = b"\n".join(self.rows)
        self.assertEqual([UI_DOCUMENTS[1]], self.bad_links(fields, self.golden(fields)))

    def test_golden_rejects_a_prior_field_fixture(self):  # PT-OPS-ORIGIN-PRO003
        fields = b"\n".join(self.rows)
        self.assertEqual(
            ["fields-ui234-236.tsv"], self.bad_links(fields, self.golden(fields + b"\n"))
        )

    def test_required_links_are_unique_and_present(self):  # PT-OPS-ORIGIN-PRO004
        fields = b"\n".join(self.rows)
        duplicate = fields + b"\n" + self.rows[1]
        unexpected = fields + b"\n# source-sha256 other.md=" + sha256(b"unexpected input")
        with self.subTest("missing golden link"):
            self.assertEqual(["fields-ui234-236.tsv"], self.bad_links(fields, b""))
        with self.subTest("duplicate design link"):
            self.assertEqual([UI_DOCUMENTS[1]], self.bad_links(duplicate, self.golden(duplicate)))
        with self.subTest("unexpected design link"):
            self.assertEqual([None], self.bad_links(unexpected, self.golden(unexpected)))
