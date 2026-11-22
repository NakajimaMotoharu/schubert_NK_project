import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "generate_maven_sbom.sh"
MODULES = ("protocol", "storage", "bootstrap", "api", "web", "batch")
STAMP = "2026-11-22T00:00:00Z"
FIXTURE = b'{"fixture": "software bom"}\n'


class GenerateMavenSbomTest(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="sbom worktree ")
        self.addCleanup(work.cleanup)
        self.root = Path(work.name).resolve()
        self.repository = self.root / "isolated repository"
        self.repository.mkdir()
        (self.root / "pom.xml").touch()
        for module in MODULES:
            path = self.root / "src" / f"schubert-nk-{module}"
            path.mkdir(parents=True)
            (path / "pom.xml").touch()
        self.wrapper = self.root / "mvnw"
        self.wrapper.write_text(
            """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

arguments = sys.argv[1:]
Path('arguments.json').write_text(json.dumps(arguments), encoding='utf-8')
if os.environ.get('NK_SIMULATED_MAVEN_OUTCOME') == 'exit':
    sys.exit(41)
if os.environ.get('NK_SIMULATED_MAVEN_OUTCOME') != 'no-output':
    destination = next(a.split('=', 1)[1] for a in arguments if a.startswith('-DoutputDirectory='))
    (Path(destination) / 'software-bom.json').write_text('{"fixture": "software bom"}\\n', encoding='utf-8')
""",
            encoding="utf-8",
        )
        self.wrapper.chmod(0o700)

    def invoke(self, *args, output="success"):
        env = dict(os.environ, NK_SIMULATED_MAVEN_OUTCOME=output)
        return subprocess.run(
            ["bash", str(SCRIPT), *map(str, args)],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )

    def test_sbom008_fixed_direct_goal_and_arguments(self):
        for module in MODULES:
            with self.subTest(module=module):
                result = self.invoke(module, self.repository, STAMP)
                self.assertEqual(0, result.returncode, result.stderr)
                artifact = Path(result.stdout.strip())
                self.assertEqual(FIXTURE, artifact.read_bytes())
                self.assertEqual(
                    self.root / "src" / f"schubert-nk-{module}" / "target",
                    artifact.parent.parent,
                )
                self.assertEqual(
                    [
                        "--batch-mode",
                        "--no-transfer-progress",
                        "--strict-checksums",
                        f"-Dmaven.repo.local={self.repository}",
                        "-pl",
                        f"src/schubert-nk-{module}",
                        "org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeBom",
                        "-DschemaVersion=1.6",
                        "-DoutputFormat=json",
                        "-DoutputName=software-bom",
                        f"-DoutputDirectory={artifact.parent}",
                        f"-Dproject.build.outputTimestamp={STAMP}",
                        "-DincludeCompileScope=true",
                        "-DincludeProvidedScope=true",
                        "-DincludeRuntimeScope=true",
                        "-DincludeTestScope=false",
                        "-DincludeSystemScope=false",
                        "-DincludeBomSerialNumber=false",
                        "-DdetectUnusedForOptionalScope=false",
                        "-Dcyclonedx.skipAttach=true",
                    ],
                    json.loads((self.root / "arguments.json").read_bytes()),
                )

    def test_sbom009_invalid_arguments_never_invoke_maven(self):
        invalid_arguments = (
            ("protocol",),
            ("../storage", self.repository, STAMP),
            ("storage", self.repository, ""),
            ("storage", self.repository / "missing", STAMP),
        )
        for args in invalid_arguments:
            with self.subTest(args=args):
                self.assertNotEqual(0, self.invoke(*args).returncode)
                self.assertFalse((self.root / "arguments.json").exists())

    def test_sbom010_forwards_maven_failure_and_preserves_previous_output(self):
        first = self.invoke("protocol", self.repository, STAMP)
        previous = Path(first.stdout.strip())
        self.assertEqual(0, first.returncode, first.stderr)
        failure = self.invoke("protocol", self.repository, STAMP, output="exit")
        self.assertEqual(41, failure.returncode)
        self.assertEqual("", failure.stdout)
        self.assertEqual(FIXTURE, previous.read_bytes())

    def test_sbom011_success_without_artifact_is_rejected(self):
        result = self.invoke("protocol", self.repository, STAMP, output="no-output")
        self.assertEqual(1, result.returncode)
        self.assertIn("produced no software BOM", result.stderr)
        self.assertEqual("", result.stdout)

    def test_sbom012_rejects_target_symlink_before_work(self):
        elsewhere = self.root / "previous"
        elsewhere.mkdir()
        target = self.root / "src" / "schubert-nk-protocol" / "target"
        target.symlink_to(elsewhere, target_is_directory=True)
        result = self.invoke("protocol", self.repository, STAMP)
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "arguments.json").exists())
        self.assertEqual([], list(elsewhere.iterdir()))


if __name__ == "__main__":
    unittest.main()
