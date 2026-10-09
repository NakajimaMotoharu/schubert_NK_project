import java.util.*;
/** SSC235 independent fixed parent/namespace/failure ownership literals; no VM actions. */
public final class Pg778FailedRecoveryTest {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("fixed failed758 vector "+count);}
  public static void main(String[] args)throws Exception{
    check(Pg778FailedRecovery.names().size()==41&&Pg778FailedRecovery.retiredNames().size()==39);
    var expected=new HashSet<String>();expected.add("epoch.current");
    for(String epoch:List.of("3c5cdcc5-204c-40fd-a731-996c6cd859e8","41691d5c-68c5-40c9-9bcc-899ce341df6b","538fe967-f9cb-4770-a03c-9bab715d0fdc","a3fd90d9-7470-4695-9ee8-c818fe19e42d","a46f1379-6025-4850-9930-658a72b0fa70","c84f3015-5f29-4844-868b-57de02b1b3fc","e45cbbc0-3eea-4b3b-bd00-2bb39e3ecc19","f5a2d1aa-3879-4f21-8e48-cfb40e48b677","e9f11f1c-f087-458a-aad0-8c1e4e140571"))for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))expected.add(epoch+suffix);
    expected.add("0a87a07d-09cf-478d-b276-180df3977e6f.owner");expected.add("0a87a07d-09cf-478d-b276-180df3977e6f.permit");
    check(expected.equals(Pg778FailedRecovery.retiredNames()));
    expected.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent");expected.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent");check(expected.equals(Pg778FailedRecovery.names()));
    var parent=new HashMap<String,String>();for(String k:Pg410KnownAuthRecovery.FIELDS)parent.put(k,"");
    parent.putAll(Map.of("InvocationID","e4093109ab234700b61dd45711126e4e","Result","timeout","ExecMainCode","1","ExecMainStatus","143","ActiveState","failed","SubState","failed","MainPID","0","ControlPID","0","Job",""));
    check(Pg778FailedRecovery.parentValue(parent));check(!Pg778FailedRecovery.parentValue(null));
    for(String key:parent.keySet()){
      var value=new HashMap<>(parent);value.remove(key);check(!Pg778FailedRecovery.parentValue(value));
      value=new HashMap<>(parent);value.put(key,null);check(!Pg778FailedRecovery.parentValue(value));
    }
    for(String key:List.of("InvocationID","Result","ExecMainCode","ExecMainStatus","ActiveState","SubState","MainPID","ControlPID","Job")){
      var value=new HashMap<>(parent);value.put(key,"foreign");check(!Pg778FailedRecovery.parentValue(value));
    }
    check(Pg778FailedRecovery.businessTableNames().size()==24&&Pg778FailedRecovery.businessTableNames().contains("schubert_web_session.web_receipt_references"));
    Pg778FailedRecovery.configureSigned();check(Pg387TrustedDeployment.expectedSqlCount==28&&Pg387TrustedDeployment.expectedHistoryCount()==29);
    check(Pg387TrustedDeployment.LABEL.equals("PG750")&&Pg387TrustedDeployment.SOURCE.equals("8d4b68b4f1449932ebe506aaf08e584bbfea8dd2"));
    for(String phase:List.of("DATABASE_BODY","REFERENCE_ACQUIRE","REFERENCE_CLOSE","DATABASE_SCOPE_CLOSE","A_SCOPE_CLOSE","M_SCOPE_CLOSE"))for(boolean changed:List.of(false,true))for(boolean secondary:List.of(false,true)){
      var failure=new Exception("literal");if(secondary)failure.addSuppressed(new Exception("literal secondary"));
      check(Pg778FailedRecovery.retainRequired(phase,changed,failure)==(changed||secondary||!phase.equals("DATABASE_BODY")));
    }
    System.out.println("PG778_JAVA_ORACLE assertions="+count+" independent=true nativeMutation0=true productionPT0=true");
  }
}
