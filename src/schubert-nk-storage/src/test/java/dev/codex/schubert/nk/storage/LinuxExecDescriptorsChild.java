package dev.codex.schubert.nk.storage;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** Test-only composed Production primitives, not root/current-permit admission. */
public final class LinuxExecDescriptorsChild {
  private LinuxExecDescriptorsChild() {}

  public static void main(String[] args) throws Exception {
    try (var directory =
            OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of(args[0]));
        var executable =
            OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/usr/bin"))) {
      directory.atExistingEntryHandle(
          "lock",
          file ->
              LinuxFileLock.create()
                  .tryExclusiveForStartup(
                      file,
                      lock ->
                          LinuxSealedProof.create()
                              .withProof(
                                  "PUBLIC-STARTUP-PROOF".getBytes(StandardCharsets.US_ASCII),
                                  proof ->
                                      executable.atExistingEntryHandle(
                                          "python3.14",
                                          held -> {
                                            LinuxExecDescriptors.create()
                                                .withInherited(
                                                    lock,
                                                    proof,
                                                    () ->
                                                        LinuxProcessExec.create()
                                                            .replace(
                                                                held,
                                                                List.of(
                                                                    "python3.14",
                                                                    "-u",
                                                                    "-c",
                                                                    "import os,fcntl,sys; assert fcntl.fcntl(128,fcntl.F_GETFD)==0; assert fcntl.fcntl(129,fcntl.F_GETFD)==0; assert fcntl.fcntl(129,fcntl.F_GET_SEALS)==15; assert os.pread(129,20,0)==b'PUBLIC-STARTUP-PROOF'; print('PID='+str(os.getpid())+' INHERITED=128,129'); assert sys.stdin.readline()=='\\n'"),
                                                                Map.of()));
                                            throw new AssertionError("replacement cannot return");
                                          }))));
      throw new AssertionError("replacement cannot return");
    }
  }
}
