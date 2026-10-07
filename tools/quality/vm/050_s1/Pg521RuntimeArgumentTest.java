/** PT-OPS-PG521-ARG: null/empty/unknown CLI before all external ownership and filesystem IO. */
public final class Pg521RuntimeArgumentTest {
  private Pg521RuntimeArgumentTest() {}
  public static void main(String[] ignored)throws Exception {
    String[][] cases={null,new String[0],new String[]{null},new String[]{""},new String[]{"retire"},new String[]{"prepare","foreign"}};
    int checks=0;
    for(var value:cases) {
      try{Pg521RuntimeResume.main(value);throw new AssertionError("unapproved argv accepted");}
      catch(IllegalStateException expected){checks++;}
    }
    System.out.println("PG521_ARGUMENT_ORACLE independentAssertions="+checks+" nullNpe0=true ownershipActions0=true");
  }
}
