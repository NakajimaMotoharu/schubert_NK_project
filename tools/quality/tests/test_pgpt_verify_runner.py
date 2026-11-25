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
OTHER_RUN = "PT-WEB-20990102-02"


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
            'printf "%s\\n" "${MAVEN_ARGS-unset}" > "$PGPT_FIXTURE_STATE/maven-args"\n'
            'printf "%s\\n" "${_JAVA_OPTIONS-unset}" > "$PGPT_FIXTURE_STATE/java-options"\n'
            'if [ -e "$PGPT_FIXTURE_STATE/change-head" ]; then\n'
            '  git commit -q --allow-empty -m "Different source during build"\n'
            "fi\n"
            'if [ -e "$PGPT_FIXTURE_STATE/change-branch" ]; then\n'
            '  git switch -qc dev-other\n'
            "fi\n"
            'if [ -e "$PGPT_FIXTURE_STATE/add-input" ]; then\n'
            '  mkdir -p src\n'
            '  printf "%s\\n" "local generated input" > src/generated-fixture.txt\n'
            "fi\n"
            'if [ -e "$PGPT_FIXTURE_STATE/add-target" ]; then\n'
            '  mkdir -p target\n'
            '  printf "%s\\n" "local generated output" > target/result.txt\n'
            "fi\n"
            'if [ -e "$PGPT_FIXTURE_STATE/fail-build" ]; then exit 9; fi\n'
        )
        wrapper.chmod(0o700)
        (self.tool_dir / "pgpt_reactor_junit.py").write_text(
            "import os, subprocess, sys\n"
            "from pathlib import Path\n"
            "state = Path(os.environ['PGPT_FIXTURE_STATE'])\n"
            "(state / 'collector').write_text(str(Path.cwd()) + '\\n' + sys.argv[2])\n"
            "if (state / 'capture-add-input').exists():\n"
            "    Path('capture-generated.txt').write_text('fixture input during capture')\n"
            "if (state / 'capture-change-branch').exists():\n"
            "    subprocess.run(['git', 'switch', '-qc', 'dev-during-capture'], check=True)\n"
            "if (state / 'capture-restrict-index').exists():\n"
            "    subprocess.run(['git', 'update-index', '--skip-worktree', 'mvnw'], check=True)\n"
        )
        self.git("init", "-q", "--initial-branch=dev-fixture")
        self.git("config", "user.name", "PGPT fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", ".")
        self.git("commit", "-qm", "Verification fixture")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True,
                              check=True)

    def invoke(self, run=RUN_ID, launcher=None):
        return subprocess.run(["sh", str(launcher or self.launcher), run], cwd=self.root, env=self.env,
                              capture_output=True, text=True, timeout=10)

    def marker(self, suffix, run=RUN_ID):
        return self.records / f"{run}.{suffix}"

    def test_001_runs_in_selected_clean_checkout_from_another_directory(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.commit, self.marker("commit").read_text().strip())
        self.assertEqual("dev-fixture", self.marker("branch").read_text().strip())
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

    def test_index_flags_on_selected_input_prevent_claim_and_build(self):
        for flag, run in (("assume-unchanged", RUN_ID), ("skip-worktree", OTHER_RUN)):
            with self.subTest(flag=flag):
                self.git("update-index", "--" + flag, "mvnw")
                try:
                    self.assertEqual(1, self.invoke(run).returncode)
                    self.assertFalse(self.marker("claim", run).exists())
                    self.assertFalse((self.state / "builds").exists())
                finally:
                    self.git("update-index", "--no-" + flag, "mvnw")

    def test_incomplete_index_visibility_after_capture_cannot_publish_success(self):
        (self.state / "capture-restrict-index").touch()
        self.assertEqual(1, self.invoke().returncode)
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertTrue((self.state / "collector").exists())

    def test_003_concurrent_duplicate_has_only_one_build_and_terminal(self):
        duplicate_path = self.root / "second checkout"
        self.git("clone", "-q", "--local", str(self.repo), str(duplicate_path))
        duplicate_launcher = duplicate_path / self.launcher.relative_to(self.repo)
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
                duplicate = self.invoke(launcher=duplicate_launcher)
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

    def test_007_same_commit_different_branch_cannot_publish_success(self):
        (self.state / "change-branch").touch()
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertEqual(self.commit, self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual("dev-other", self.git("branch", "--show-current").stdout.strip())
        self.assertEqual("dev-fixture", self.marker("branch").read_text().strip())
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertFalse((self.state / "collector").exists())

    def test_008_distinct_ids_cannot_share_running_checkout(self):
        other = self.root / "different checkout"
        self.git("clone", "-q", "--local", str(self.repo), str(other))
        first_env = dict(self.env, PGPT_FIXTURE_WAIT_FOR_SOURCE="1")
        with subprocess.Popen(["sh", str(self.launcher), RUN_ID], cwd=self.root, env=first_env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as first:
            try:
                expiry = time.monotonic() + 5
                while not (self.state / "before-source").exists() and first.poll() is None:
                    self.assertLess(time.monotonic(), expiry)
                    time.sleep(0.02)
                self.assertTrue(self.marker("claim").is_dir())
                self.assertNotEqual(0, self.invoke(OTHER_RUN).returncode)
                self.assertFalse(self.marker("claim", OTHER_RUN).exists())
                self.assertEqual(0, self.invoke(OTHER_RUN, other / self.launcher.relative_to(self.repo)).returncode)
                self.assertEqual(other, Path((self.state / "builds").read_text().strip()))
            finally:
                (self.state / "release").touch()
                _, stderr = first.communicate(timeout=10)
        self.assertEqual(0, first.returncode, stderr)
        self.assertEqual("0", self.marker("exit").read_text().strip())
        self.assertEqual("0", self.marker("exit", OTHER_RUN).read_text().strip())
        self.assertEqual([str(other), str(self.repo)], (self.state / "builds").read_text().splitlines())

    def test_009_detached_checkout_does_not_claim_run(self):
        self.git("checkout", "-q", "--detach", self.commit)
        self.assertNotEqual(0, self.invoke().returncode)
        self.assertEqual([], list(self.records.iterdir()))
        self.assertFalse((self.state / "builds").exists())

    def test_010_new_untracked_input_stops_capture_even_if_default_status_hides_it(self):
        self.git("config", "status.showUntrackedFiles", "no")
        (self.state / "add-input").touch()
        result = self.invoke()
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertEqual(self.commit, self.marker("commit").read_text().strip())
        self.assertFalse((self.state / "collector").exists())
        self.assertEqual(
            "local generated input\n", (self.repo / "src/generated-fixture.txt").read_text()
        )

    def test_011_ignored_build_output_preserves_a_clean_checkout(self):
        (self.repo / ".gitignore").write_text("/target/\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "Ignore generated test output")
        source = self.git("rev-parse", "HEAD").stdout.strip()
        (self.state / "add-target").touch()
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("0", self.marker("exit").read_text().strip())
        self.assertEqual(source, self.marker("commit").read_text().strip())
        self.assertTrue((self.state / "collector").is_file())
        self.assertEqual("local generated output\n", (self.repo / "target/result.txt").read_text())

    def test_012_full_verification_does_not_inherit_caller_maven_args(self):
        self.env["MAVEN_ARGS"] = "-DfixtureMarker=caller-default"
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("unset\n", (self.state / "maven-args").read_text())
        self.assertEqual("0", self.marker("exit").read_text().strip())

    def test_013_full_verification_does_not_inherit_hotspot_defaults(self):
        self.env["_JAVA_OPTIONS"] = "-Dfile.encoding=US-ASCII"
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("unset\n", (self.state / "java-options").read_text())
        self.assertEqual("0", self.marker("exit").read_text().strip())


    def test_014_input_added_during_capture_cannot_publish_a_verified_terminal(self):
        (self.state / "capture-add-input").touch()
        completed = self.invoke()
        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertEqual("fixture input during capture",
                         (self.repo / "capture-generated.txt").read_text())
        self.assertTrue((self.state / "collector").is_file())
        self.assertTrue(self.marker("claim").is_dir())

    def test_015_branch_changed_during_capture_cannot_publish_a_verified_terminal(self):
        (self.state / "capture-change-branch").touch()
        completed = self.invoke()
        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertEqual("1", self.marker("exit").read_text().strip())
        self.assertEqual(self.commit, self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual("dev-during-capture", self.git("branch", "--show-current").stdout.strip())
        self.assertEqual("dev-fixture", self.marker("branch").read_text().strip())
        self.assertTrue((self.state / "collector").is_file())


if __name__ == "__main__":
    unittest.main()
