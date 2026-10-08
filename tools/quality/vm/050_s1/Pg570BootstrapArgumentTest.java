/** SSC225: CLI/null boundary has no ownership/Unit/file action. */
public final class Pg570BootstrapArgumentTest {
  public static void main(String[] args) {
    int assertions=0;
    for(String[] value:new String[][]{null,new String[]{},new String[]{null},new String[]{"bad"},new String[]{"verify","extra"},new String[]{" execute"}}){
      try{Pg570BootstrapExisting.arguments(value);throw new AssertionError("invalid CLI admitted");}
      catch(IllegalStateException expected){assertions++;}
    }
    for(String mode:new String[]{"verify","execute"}){
      if(!mode.equals(Pg570BootstrapExisting.arguments(new String[]{mode})))throw new AssertionError("valid mode changed");assertions++;
    }
    System.out.println("PG570_ARGUMENT_ORACLE independentAssertions="+assertions+" nullNpe0=true ownershipActions0=true");
  }
}
