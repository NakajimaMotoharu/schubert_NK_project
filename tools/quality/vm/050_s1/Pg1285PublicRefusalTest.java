package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;

/** BUG1073/YKT842 independent public-boundary values, no Production-generated expected. */
public final class Pg1285PublicRefusalTest {
  private Pg1285PublicRefusalTest() {}

  public static void main(String[] args) {
    if (!Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(
        new StorageIoException(StorageIoException.Reason.UNAVAILABLE)))
      throw new AssertionError("public unavailable refusal rejected");
    if (Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(null)
        || Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(new IOException("fixed PT native capture unavailable"))
        || Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(new StorageIoException(StorageIoException.Reason.MISSING))
        || Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(new StorageIoException(StorageIoException.Reason.COLLISION)))
      throw new AssertionError("wrong public contract accepted");
    var withCause = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    withCause.initCause(new IOException("test cause must not escape"));
    var withSuppressed = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    withSuppressed.addSuppressed(new IOException("test suppressed must not escape"));
    if (Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(withCause)
        || Pg1282PhysicalPinProbe.acceptedReadWriteRefusal(withSuppressed))
      throw new AssertionError("physical diagnostic leaked across public boundary");
    System.out.println("PUBLIC_REFUSAL_7_VECTORS_PASS");
  }
}
