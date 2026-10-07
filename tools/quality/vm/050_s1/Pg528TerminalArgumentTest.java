/** PT-OPS-PG528-ARG: null/empty/unknown CLI before all external ownership and filesystem IO. */
public final class Pg528TerminalArgumentTest {
  private Pg528TerminalArgumentTest() {}
  public static void main(String[] ignored)throws Exception {
    String[][] cases={null,new String[0],new String[]{null},new String[]{""},new String[]{"retire"},new String[]{"readback","foreign"}};
    int checks=0;
    for(var value:cases) {
      try{Pg528TerminalReadback.main(value);throw new AssertionError("unapproved argv accepted");}
      catch(IllegalStateException expected){checks++;}
    }
    System.out.println("PG528_ARGUMENT_ORACLE independentAssertions="+checks+" nullNpe0=true ownershipActions0=true");
  }
}
