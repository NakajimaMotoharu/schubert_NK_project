import java.util.*;

/** MIG202008 independent argument boundary; not permission, guest mutation or PT credit. */
public final class Pg491PendingDeploymentTest {
  public static void main(String[] ignored){
    String s="a".repeat(40),d="b".repeat(64);
    String[][] refused={null,new String[0],new String[]{s},new String[]{null,d},new String[]{s,null},new String[]{s,d,"extra"},new String[]{"x".repeat(40),d},new String[]{s,"X".repeat(64)}};
    for(var value:refused)if(Pg491PendingDeployment.arguments(value))throw new AssertionError("foreign arguments accepted");
    if(!Pg491PendingDeployment.arguments(new String[]{s,d}))throw new AssertionError("fixed demand refused");
    if(!Pg491PendingDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG489"))throw new AssertionError("foreign target");
    System.out.println("PG491_PENDING_CALLER_ORACLE independentAssertions=10 actual0=true vmAuthority0=true");
  }
}
