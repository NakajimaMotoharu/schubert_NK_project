"""Exercise the verification launcher against a disposable Git fixture."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest


RUNNER = Path(__file__).resolve().parents[1] / "030_run_pgpt_verify.sh"
RUN_ID = "PT-WEB-20990102-01"


class VerifyRunnerTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="pgpt-verify-fixture-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.repo = self.root / "isolated checkout"
        self.tool_dir = self.repo / "tools/quality"
        self.tool_dir.mkdir(parents=True)
        self.records = self.root / "records"
        self.records.mkdir()
        self.state = self.root / "state"
        self.state.mkdir()
        self.launcher = self.tool_dir / RUNNER.name

        # Keep the fixed production marker contract out of the shared /tmp namespace.
        shell = RUNNER.read_text()
        marker = 'record="/tmp/$run_id"'
        self.assertEqual(1, shell.count(marker))
        self.launcher.write_text(shell.replace(marker, f'record="{self.records}/$run_id"'))

        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        date = bin_dir / "date"
        date.write_text(
            "#!/bin/sh\n"
            'if [ "$1" = +%Y%m%d ]; then echo 20990102; '
            "else echo 2099-01-02T12:00:00+09:00; fi\n"
        )
        date.chmod(0o700)
        git_bin = shutil.which("git")
        self.assertIsNotNone(git_bin)
        git = bin_dir / "git"
        git.write_text(
            "#!/bin/sh\n"
            'if [ "${PGPT_FIXTURE_WAIT_FOR_SOURCE:-0}" = 1 ]'
            ' && [ "$1" = rev-parse ] && [ "$2" = HEAD ]; then\n'
            '  touch "$PGPT_FIXTURE_STATE/before-source"\n'
            '  while [ ! -e "$PGPT_FIXTURE_STATE/release" ]; do sleep 0.02; done\n'
            "fi\n"
            'exec "$PGPT_FIXTURE_GIT" "$@"\n'
        )
        git.chmod(0o700)
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PGPT_FIXTURE_STATE": str(self.state),
            "PGPT_FIXTURE_GIT": git_bin,
        }
        wrapper = self.repo / "mvnw"
        wrapper.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            'pwd -P >> "$PGPT_FIXTURE_STATE/builds"\n'
            'if [ -e "$PGPT_FIXTURE_STATE/change-head" ]; then\n'
            '  git commit -q --allow-empty -m "Different source during build"\n'
            "fi\n"
            'if [ -e "$PGPT_FIXTURE_STATE/fail-build" ]; then exit 9; fi\n'
        )
        wrapper.chmod(0o700)
        (self.tool_dir / "pgpt_reactor_junit.py").write_text(
            "import os, sys\n"
            "from pathlib import Path\n"
            "state = Path(os.environ['PGPT_FIXTURE_STATE'])\n"
            "(state / 'collector').write_text(str(Path.cwd()) + '\\n' + sys.argv[2])\n"
        )
        self.git("init", "-q")
        self.git("config", "user.name", "PGPT fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", ".")
        self.git("commit", "-qm", "Verification fixture")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True,
                              check=True)

    def invoke(self):
        return subprocess.run(["sh", str(self.launcher), RUN_ID], cwd=self.root, env=self.env,
                              capture_output=True, text=True, timeout=10)

    def marker(self, suffix):
        return self.records / f"{RUN_ID}.{suffix}"

    def test_001_runs_in_selected_clean_checkout_from_another_directory(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.commit, self.marker("commit").read_text().strip())
        self.assertEqual("0", self.marker("exit").read_text().strip())
        self.assertEqual([str(self.repo)], (self.state / "builds").read_text().splitlines())
        self.assertEqual([str(self.repo), self.commit],
                         (self.state / "collector").read_text().splitlines())
        self.assertTrue(self.marker("claim").is_dir())

    def test_002_dirty_checkout_cannot_claim_or_run(self):
        (self.repo / "untracked").write_text("fixture to preserve")
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertEqual([], list(self.records.iterdir()))
        self.assertFalse((self.state / "builds").exists())

    def test_003_concurrent_duplicate_has_only_one_build_and_terminal(self):
        first_env = dict(self.env, PGPT_FIXTURE_WAIT_FOR_SOURCE="1")
        with subprocess.Popen(["sh", str(self.launcher), RUN_ID], cwd=self.root, env=first_env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as first:
            try:
                expiry = time.monotonic() + 5
                while not (self.state / "before-source").exists() and first.poll() is None:
                    self.assertLess(time.monotonic(), expiry)
                    time.sleep(0.02)
                self.assertTrue(self.marker("claim").is_dir())
                self.assertFalse(self.marker("commit").exists())
                self.assertFalse(self.marker("exit").exists())
                duplicate = self.invoke()
                self.assertNotEqual(0, duplicate.returncode)
                self.assertFalse(self.marker("exit").exists())
            finally:
                (self.state / "release").touch()
                _, stderr = first.communicate(timeout=10)
        self.assertEqual(0, first.returncode, stderr)
        self.assertEqual([str(self.repo)], (self.state / "builds").read_text().splitlines())
        self.assertEqual("0", self.marker("exit").read_text().strip())

    def test_004_existing_marker_is_preserved_without_a_new_claim(self):
        self.marker("commit").write_text("original source\n")
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertEqual("original source\n", self.marker("commit").read_text())
        self.assertFalse(self.marker("claim").exists())
        self.assertFalse((self.state / "builds").exists())

    def test_005_changed_head_cannot_publish_success_for_the_original_commit(self):
        (self.state / "change-head").touch()
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertNotEqual(self.commit, self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual(self.commit, self.marker("commit").read_text().strip())
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertFalse((self.state / "collector").exists())

    def test_006_failed_build_cannot_be_restarted_with_the_same_id(self):
        (self.state / "fail-build").touch()
        self.assertEqual(9, self.invoke().returncode)
        self.assertEqual("9", self.marker("exit").read_text().strip())
        self.assertFalse((self.state / "collector").exists())
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertEqual([str(self.repo)], (self.state / "builds").read_text().splitlines())


if __name__ == "__main__":
    unittest.main()
