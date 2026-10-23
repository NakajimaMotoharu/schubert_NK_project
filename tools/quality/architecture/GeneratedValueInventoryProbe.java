/** Owned metadata-only tool probe. Any target initialization fails instead of performing I/O. */
public final class GeneratedValueInventoryProbe {
  static {
    if (Boolean.parseBoolean("true")) throw new AssertionError("probe outer must not initialize");
  }

  private GeneratedValueInventoryProbe() {}

  public record BrokenRecord(int count) {
    static {
      if (Boolean.parseBoolean("true")) throw new AssertionError("probe record must not initialize");
    }
  }

  public enum BrokenEnum {
    ONE;
    static {
      if (Boolean.parseBoolean("true")) throw new AssertionError("probe enum must not initialize");
    }
  }
}
