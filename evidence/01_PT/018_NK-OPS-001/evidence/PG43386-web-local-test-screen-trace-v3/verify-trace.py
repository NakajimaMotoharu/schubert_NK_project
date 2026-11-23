"""Verify a fixed set of Web unit results against independent PT specs and canonical UI IDs."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
WEB = Path("evidence/01_PT/015_NK-WEB-001")
UI = Path("documents/200_UI/220_画面・認証/221_画面一覧・画面遷移設計.md")
CASE_TABLE = re.compile(r"^\|\s*(PT-WEB-\d{3})\s*\|\s*([^|]+?)\s*\|\s*(.+)\|$")
UI_TABLE = re.compile(r"^\|\s*(SCR-\d{3})\s*\|[^|\r\n\x60]*\x60([^\x60\r\n]+)\x60", re.M)
# These route expectations come from UI221, section 3. No route is claimed for PageViewModel.
GROUPS = {
    43366: ((4,), {}),
    43368: ((20,), {"SCR-011": "/music", "SCR-012": "/music/{category}"}),
    43370: ((16,), {"SCR-008": "/animation", "SCR-009": "/animation/main"}),
    43372: ((6,), {"SCR-004": "/scenarios", "SCR-005": "/scenarios/{game}",
                    "SCR-006": "/scenarios/{game}/{prefix}"}),
    43376: ((10, 14), {"SCR-003": "/search"}),
    43378: ((24, 30), {"SCR-014": "/logs"}),
    43382: ((8,), {"SCR-007": "/scenarios/{id}"}),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_content(revision, path):
    return subprocess.check_output(["git", "show", f"{revision}:{path}"])


def pick(path, pattern):
    return next(path.glob(pattern))


def verify_screen_routes(ui_routes, expected_routes, reported):
    if set(reported) != set(expected_routes):
        raise ValueError("reported screen IDs differ from the independent route contract")
    for screen, route in expected_routes.items():
        if ui_routes.get(screen) != route:
            raise ValueError(f"route mismatch for {screen}")


def verify(canonical):
    ui_bytes = git_content(canonical, UI)
    sections = ui_bytes.decode().split("## 3. 画面一覧\n", 1)
    assert len(sections) == 2
    screen_table = sections[1].split("\n## 4.", 1)[0]
    route_pairs = UI_TABLE.findall(screen_table)
    routes = dict(route_pairs)
    if len(routes) != len(route_pairs) or routes.get("SCR-016") != "/admin/users/new":
        raise ValueError("cannot bind canonical UI221 rows uniquely")
    for run, incorrect in ((43378, ("SCR-016",)), (43372, ("SCR-003", "SCR-004", "SCR-005"))):
        try:
            verify_screen_routes(routes, GROUPS[run][1], incorrect)
        except ValueError:
            continue
        raise ValueError(f"negative wrong-screen fixture was accepted for {run}")

    all_tests = set()
    rows = []
    proofs = []
    for run, (spec_numbers, expected_routes) in GROUPS.items():
        verify_screen_routes(routes, expected_routes, tuple(expected_routes))
        evidence = pick(OPS, f"PG{run}-*/manifest.json")
        evidence_bytes = evidence.read_bytes()
        result = json.loads(evidence_bytes)
        junit = Path(result["junit"]["xml"]["path"])
        xml_bytes = junit.read_bytes()
        assert result["junit"]["xml"]["sha256"] == sha(xml_bytes)
        xml = ElementTree.fromstring(xml_bytes)
        assert result["actualExit"] == 0 and not result["whole451"]
        assert all(xml.get(key) == "0" for key in ("errors", "failures", "skipped"))
        actual_nodes = xml.findall("testcase")
        actual = {node.get("name").split("(", 1)[0]: node.get("classname") for node in actual_nodes}
        reported = result["selectedTestIds"]
        expected = {}
        for spec_number in spec_numbers:
            path = pick(WEB, f"{spec_number:03}_*.md")
            data = path.read_bytes()
            assert data == git_content(result["source"], path)
            for line_no, line in enumerate(data.decode().splitlines(), 1):
                match = CASE_TABLE.fullmatch(line)
                if not match:
                    continue
                test, method, _ = match.groups()
                assert test not in expected and test not in all_tests
                expected[test] = (path, line_no, method.strip(), sha(line.encode()))
        assert set(expected) == set(reported)
        assert not (all_tests & expected.keys())
        assert len(actual) == len(actual_nodes) == len(expected) == int(xml.get("tests"))
        for test, (path, line_no, method, expected_sha) in sorted(expected.items()):
            saved = reported[test]
            assert method == (saved["method"] if isinstance(saved, dict) else saved)
            if isinstance(saved, dict):
                assert saved["className"] == actual[method]
            assert actual[method].startswith("dev.codex.schubert.nk.web.view.")
            rows.append((test, method, actual[method], str(path), line_no, expected_sha,
                         ",".join(expected_routes) or "SHARED", run, result["source"]))
        all_tests.update(expected)
        proofs.append({"run": run, "path": str(evidence), "sha256": sha(evidence_bytes),
                       "source": result["source"], "canonicalScreenIds": list(expected_routes),
                       "qualifiedCases": len(expected), "junitXmlSha256": sha(xml_bytes)})
    assert len(all_tests) == len(rows) == 80
    return rows, {"canonicalUi221Sha256": sha(ui_bytes), "canonicalDesignSource": canonical,
                  "groups": proofs, "wrongScreenChecksRejected": 2}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical")
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    rows, proof = verify(args.canonical)
    with args.trace.open("x", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(("TestID", "Method", "JUnitClass", "Specification", "Line",
                         "ExpectedRowSHA256", "ScreenIDs", "PG", "Source"))
        writer.writerows(rows)
    json.dump(proof, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
