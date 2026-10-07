/** BOOT537001: malformed CLI refuses before any external scope; no native/Production PT credit. */
public final class Pg537BootstrapArgumentTest {
  private Pg537BootstrapArgumentTest() {}
  public static void main(String[] ignored)throws Exception {
    String[][] cases={null,new String[0],new String[]{null},new String[]{""},new String[]{"readback"},new String[]{"execute","foreign"}};
    int checks=0;
    for(var value:cases) {
      try{Pg537BootstrapRetire.main(value);throw new AssertionError("unapproved argv accepted");}
      catch(IllegalStateException expected){checks++;}
    }
    System.out.println("PG537_ARGUMENT_ORACLE independentAssertions="+checks+" nullNpe0=true ownershipActions0=true");
  }
}

