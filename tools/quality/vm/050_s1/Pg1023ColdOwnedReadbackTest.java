public final class Pg1023ColdOwnedReadbackTest {
  static void rejected(String[] input) {
    try {Pg1023ColdOwnedReadback.arguments(input);throw new AssertionError("accepted invalid operation");}
    catch(IllegalStateException expected) { /* no I/O or authority acquired */ }
  }
  public static void main(String[] args) {
    Pg1023ColdOwnedReadback.arguments(new String[]{"verify"});
    rejected(null);rejected(new String[0]);rejected(new String[]{null});
    rejected(new String[]{"prepare"});rejected(new String[]{"execute"});
    rejected(new String[]{"verify","extra"});rejected(new String[]{"VERIFY"});
    if(!Pg1023ColdOwnedReadback.ORIGINAL.run().id().toString().equals("eeae04ea-713c-4f2d-888d-358fb4bed274")
        ||!Pg1023ColdOwnedReadback.ORIGINAL.id().toString().equals("091663ce-1cf4-47e7-8311-218ebb0c8653")
        ||!Pg1023ColdOwnedReadback.ORIGINAL.run().cutoff().toString().equals("2026-10-09T23:31:22.087768Z"))throw new AssertionError("original golden mismatch");
    System.out.println("PT-DEP-1023001 argument/original golden PASS; no VM or namespace mutation");
  }
}
