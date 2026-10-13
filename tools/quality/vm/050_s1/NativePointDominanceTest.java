import java.util.List;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.ExecutionDataStore;

/** Literal synthetic probes are independent expected values, never Production methods. */
public final class NativePointDominanceTest {
  private NativePointDominanceTest() {}

  private static ExecutionDataStore store(long id, String name, boolean... probes) {
    var v = new ExecutionDataStore();
    v.put(new ExecutionData(id, name, probes));
    return v;
  }

  private static void refused(Runnable action) {
    try {
      action.run();
    } catch (IllegalArgumentException expected) {
      return;
    }
    throw new AssertionError("independent invalid vector must be refused");
  }

  public static void main(String[] args) {
    var early = List.of(new ExecutionData(7L, "literal/Class", new boolean[] {true, false, true}));
    NativePointDominance.verify(early, store(7L, "literal/Class", true, true, true));
    NativePointDominance.verify(early, store(7L, "literal/Class", true, false, true));
    refused(() -> NativePointDominance.verify(null, store(7L, "literal/Class", true, false, true)));
    refused(() -> NativePointDominance.verify(List.of(), store(7L, "literal/Class", true)));
    refused(() -> NativePointDominance.verify(early, null));
    refused(() -> NativePointDominance.verify(early, store(8L, "literal/Class", true, true, true)));
    refused(() -> NativePointDominance.verify(early, store(7L, "foreign/Class", true, true, true)));
    refused(() -> NativePointDominance.verify(early, store(7L, "literal/Class", true, true)));
    refused(
        () -> NativePointDominance.verify(early, store(7L, "literal/Class", false, true, true)));
    refused(
        () -> NativePointDominance.verify(early, store(7L, "literal/Class", true, true, false)));
    System.out.println("literalMonotonic10Vectors=true");
  }
}
