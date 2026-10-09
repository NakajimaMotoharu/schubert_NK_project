import java.util.*;
/** Closed actual readonly profile; server values remain actual, never mocked into VM acceptance. */
public final class Pg797DatabaseProbeTest{
  public static void main(String[]args)throws Exception{
    if(Pg797DatabaseProbe.retiredNames().size()!=39)throw new AssertionError("literal39");
    var parent=new HashMap<String,String>();for(String k:Pg410KnownAuthRecovery.FIELDS)parent.put(k,"");
    parent.putAll(Map.of("InvocationID","e4093109ab234700b61dd45711126e4e","Result","timeout","ExecMainCode","1","ExecMainStatus","143","ActiveState","failed","SubState","failed","MainPID","0","ControlPID","0","Job",""));
    if(!Pg797DatabaseProbe.parentValue(parent)||Pg797DatabaseProbe.parentValue(null))throw new AssertionError("failed143 not restored");
    Pg797OwnedDatabaseTest.main(args);
    System.out.println("PG797_PROFILE_ORACLE all39=true noActualDatabaseValuesMinted=true productionPT0=true");
  }
}
