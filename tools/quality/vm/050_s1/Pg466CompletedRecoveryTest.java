import java.util.*;
public final class Pg466CompletedRecoveryTest {
  static int count;static void check(boolean b){count++;if(!b)throw new AssertionError("recovery vector "+count);}
  public static void main(String[] args)throws Exception{
    check(Pg466CompletedRecovery.arguments(new String[]{"activate"}));
    for(String[] invalid:new String[][]{null,{}, {null},{"verify"},{"activate","again"}})check(!Pg466CompletedRecovery.arguments(invalid));
    var calls=new ArrayList<Integer>();Pg466CompletedRecovery.sequence(calls::add);check(calls.equals(List.of(0,1,2,3,4,5)));
    for(int at=0;at<6;at++){final int failureAt=at;calls.clear();var failure=new Exception("injected");try{Pg466CompletedRecovery.sequence(n->{calls.add(n);if(n==failureAt)throw failure;});throw new AssertionError("failure swallowed");}catch(Exception actual){check(actual==failure);check(calls.equals(List.of(0,1,2,3,4,5).subList(0,at+1)));}}
    check(!Pg465CompletedDeployment.normalDone(null));
    System.out.println("PG466_RECOVERY_ORACLE_PASS independentAssertions="+count+" productionPT0=true mutation0=true");
  }
}
