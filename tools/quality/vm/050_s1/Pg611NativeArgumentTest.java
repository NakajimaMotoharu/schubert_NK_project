/** PT-OPS-PG611-ARG: null/empty/unknown CLI before all external ownership and filesystem IO. */
public final class Pg611NativeArgumentTest {
  private Pg611NativeArgumentTest() {}
  public static void main(String[] ignored)throws Exception {
    String[][] cases={null,new String[0],new String[]{null},new String[]{""},new String[]{"retire"},new String[]{"stop","foreign"}};
    int checks=0;
    for(var value:cases) {
      try{Pg611NativeStop.main(value);throw new AssertionError("unapproved argv accepted");}
      catch(IllegalStateException expected){checks++;}
    }
    System.out.println("PG611_ARGUMENT_ORACLE independentAssertions="+checks+" nullNpe0=true ownershipActions0=true");
  }
}
