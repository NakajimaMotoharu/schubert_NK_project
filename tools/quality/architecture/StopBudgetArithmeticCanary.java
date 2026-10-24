/** Independent Java long vectors only; no production class/Thread/provider/resource is executed. */
public final class StopBudgetArithmeticCanary {
  private StopBudgetArithmeticCanary() {}

  public static void main(String[] arguments) {
    long wrapped = Long.MIN_VALUE - Long.parseLong("1");
    if (wrapped != Long.MAX_VALUE || Math.min(wrapped, 1_000L) != 1_000L)
      throw new AssertionError("independent Java overflow vector differs");
    for (long initial : new long[] {0, -1, Long.MIN_VALUE}) {
      if (initial > 0) throw new AssertionError("independent nonpositive vector differs");
    }
    long frozen = 2;
    if (Math.min(frozen - 1, 50L) != 1 || Math.min(frozen - 2, 50L) != 0)
      throw new AssertionError("independent frozen budget vector differs");
    System.out.println("WRAP_MAX=true; OLD_POSITIVE=1000; NONPOSITIVE=3; FROZEN=1,0");
  }
}
