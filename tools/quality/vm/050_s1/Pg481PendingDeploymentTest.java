/** BREC198010 caller argument negatives, public independent literal only. */
public final class Pg481PendingDeploymentTest {
  public static void main(String[] args){
    String[][] refused={null,new String[0],new String[]{null},new String[]{"verify"},new String[]{"activate","extra"},new String[]{"resume"}};
    for(var value:refused)if(Pg481PendingDeployment.arguments(value))throw new AssertionError("foreign arguments accepted");
    if(!Pg481PendingDeployment.arguments(new String[]{"activate"}))throw new AssertionError("fixed action refused");
    System.out.println("PG481_PENDING_CALLER_ORACLE assertions=7 actual0=true vmAuthority0=true");
  }
}
