package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * The fixed Web/API root issuer's single A owner. A fresh root identity and all following read-only
 * gate observations must stay inside the borrowed A callback. This still never issues startup
 * authority, proof, process replacement or readiness; the caller remains fail-closed. NK-OPS-001;
 * SYS002/004,OPS009; UI212/251/253; SS341/342/343; SSC086..089; PG372/PT-OPS-RASCOPE001..006; 471
 * R1/D04/D05.
 */
@NullMarked
final class RootServiceAdmissionScope {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Work {
    void execute(int borrowedAdmissionFd) throws IOException;
  }

  @FunctionalInterface
  interface Exclusive {
    Optional<Boolean> execute(Work work) throws IOException;
  }

  private RootServiceAdmissionScope() {}

  static void execute(RootStartupContext root, RootStartupContext.Snapshot expected, Work work)
      throws IOException {
    Objects.requireNonNull(root, "root actor");
    Objects.requireNonNull(expected, "fixed root snapshot");
    execute(
        () -> root.recheck(expected),
        inner ->
            StartupAdmissionFile.create()
                .tryExclusive(
                    reserved -> {
                      inner.execute(reserved);
                      return Boolean.TRUE;
                    }),
        work);
  }

  static void execute(Gate root, Exclusive admission, Work work) throws IOException {
    Objects.requireNonNull(root, "root identity gate");
    Objects.requireNonNull(admission, "fixed startup A");
    Objects.requireNonNull(work, "A-held root preflight");
    root.verify();
    var result =
        Objects.requireNonNull(
            admission.execute(
                descriptor -> {
                  root.verify();
                  if (descriptor < 128 || descriptor > 65535)
                    throw new IOException("startup admission unavailable");
                  work.execute(descriptor);
                  root.verify();
                }),
            "A acquisition result");
    if (result.isEmpty() || !result.orElseThrow())
      throw new IOException("startup admission unavailable");
    root.verify();
  }
}
