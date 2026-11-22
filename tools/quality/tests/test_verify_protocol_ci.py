"""Local Maven command contract for PT-OPS-CI-PRO001..004."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "verify_protocol_ci.sh"


class VerifyProtocolCiTest(unittest.TestCase):
    def setUp(self):
        sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(sandbox.cleanup)
        self.root = Path(sandbox.name).resolve()
        self.repository = self.root / "verified Maven cache"
        self.repository.mkdir()
        self.module = self.root / "src/schubert-nk-protocol"
        self.module.mkdir(parents=True)
        for directory in (self.root, self.module):
            (directory / "pom.xml").write_text("<project/>\n", encoding="utf-8")
        wrapper = self.root / "mvnw"
        wrapper.write_text(
            '#!/usr/bin/env bash\n'
            'printf "%s\\0" "$@" > observed.args\n'
            'printf "%s" "${MAVEN_ARGS-}" > inherited.args\n'
            'exit "${FIXTURE_MAVEN_EXIT:-0}"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o700)

    def invoke(self, *arguments, status=0):
        return subprocess.run(
            [str(SCRIPT), *map(str, arguments)],
            cwd=self.root,
            env=dict(os.environ, MAVEN_ARGS="-pl unrelated", FIXTURE_MAVEN_EXIT=str(status)),
            capture_output=True,
            timeout=10,
        )

    def test_fixed_offline_module_and_maven_phase(self):
        result = self.invoke(self.repository)
        self.assertEqual(0, result.returncode, result.stderr)
        expected = [
            "--offline", "--batch-mode", "--strict-checksums", "--no-transfer-progress",
            f"-Dmaven.repo.local={self.repository}", "-DskipTests=false", "-Dmaven.test.skip=false",
            "-Dmaven.test.failure.ignore=false", "-DfailIfNoTests=true",
            "-pl", "src/schubert-nk-protocol", "verify",
        ]
        self.assertEqual(b"\0".join(arg.encode() for arg in expected) + b"\0",
                         (self.root / "observed.args").read_bytes())
        self.assertEqual(b"", (self.root / "inherited.args").read_bytes())

    def test_maven_failure_is_the_command_failure(self):
        result = self.invoke(self.repository, status=23)
        self.assertEqual(23, result.returncode)
        self.assertTrue((self.root / "observed.args").is_file())

    def test_missing_invalid_and_extra_repository_arguments(self):
        for args in ((), (self.root / "missing",), (self.repository, "package")):
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertEqual(2, result.returncode)
                self.assertFalse((self.root / "observed.args").exists())

    def test_requires_the_protocol_worktree_root(self):
        (self.module / "pom.xml").unlink()
        result = self.invoke(self.repository)
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "observed.args").exists())
