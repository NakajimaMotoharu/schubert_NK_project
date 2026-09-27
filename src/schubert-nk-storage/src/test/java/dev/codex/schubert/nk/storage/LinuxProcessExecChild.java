package dev.codex.schubert.nk.storage;

import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** External native PT only: no production bootstrap gate or privilege claim. */
public final class LinuxProcessExecChild {
  private LinuxProcessExecChild() {}

  public static void main(String[] ignored) throws Exception {
    try (var directory =
        OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/usr/bin"))) {
      directory.atExistingEntryHandle(
          "python3.14",
          file -> {
            LinuxProcessExec.create()
                .replace(
                    file,
                    List.of(
                        "python3.14",
                        "-c",
                        "import os; assert 'PGPT_EXEC_UNEXPECTED' not in os.environ; assert 'PATH' not in os.environ; print('PID=' + str(os.getpid()) + ' ENV=' + os.environ['PGPT_EXEC'])"),
                    Map.of("PGPT_EXEC", "fixture_only"));
            throw new AssertionError("successful exec cannot return");
          });
    }
  }
}
