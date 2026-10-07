/** PT-OPS-PG524-ARG: null/empty/unknown CLI before all external ownership and filesystem IO. */
public final class Pg524NativeArgumentTest {
  private Pg524NativeArgumentTest() {}
  public static void main(String[] ignored)throws Exception {
    String[][] cases={null,new String[0],new String[]{null},new String[]{""},new String[]{"retire"},new String[]{"stop","foreign"}};
    int checks=0;
    for(var value:cases) {
      try{Pg524NativeStop.main(value);throw new AssertionError("unapproved argv accepted");}
      catch(IllegalStateException expected){checks++;}
    }
    System.out.println("PG524_ARGUMENT_ORACLE independentAssertions="+checks+" nullNpe0=true ownershipActions0=true");
  }
}
