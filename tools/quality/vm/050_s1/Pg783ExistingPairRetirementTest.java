import java.util.*;
/** SSC236 independent namespace/parent/Ref-ownership tests; no real operation. */
public final class Pg783ExistingPairRetirementTest {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("existing pair vector "+count);}
  public static void main(String[] args)throws Exception{
    check(Pg783ExistingPairRetirement.quarantinedNames().size()==42);
    check(Pg783ExistingPairRetirement.retiredNames().size()==39);
    // Literal retained namespace, independent of production/helper name builders.
    var names=new HashSet<String>();names.add("epoch.current");
    for(String epoch:List.of("3c5cdcc5-204c-40fd-a731-996c6cd859e8","41691d5c-68c5-40c9-9bcc-899ce341df6b","538fe967-f9cb-4770-a03c-9bab715d0fdc","a3fd90d9-7470-4695-9ee8-c818fe19e42d","a46f1379-6025-4850-9930-658a72b0fa70","c84f3015-5f29-4844-868b-57de02b1b3fc","e45cbbc0-3eea-4b3b-bd00-2bb39e3ecc19","f5a2d1aa-3879-4f21-8e48-cfb40e48b677","e9f11f1c-f087-458a-aad0-8c1e4e140571"))
      for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))names.add(epoch+suffix);
    names.add("0a87a07d-09cf-478d-b276-180df3977e6f.owner");names.add("0a87a07d-09cf-478d-b276-180df3977e6f.permit");
    check(names.size()==39);check(names.equals(Pg783ExistingPairRetirement.retiredNames()));
    names.add("permit-start.intent");names.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent");names.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent");
    check(names.equals(Pg783ExistingPairRetirement.quarantinedNames()));
    var parent=new HashMap<String,String>();for(String k:Pg410KnownAuthRecovery.FIELDS)parent.put(k,"");
    parent.putAll(Map.of("InvocationID","e4093109ab234700b61dd45711126e4e","Result","timeout","ExecMainCode","1","ExecMainStatus","143","ActiveState","failed","SubState","failed","MainPID","0","ControlPID","0","Job",""));
    check(Pg783ExistingPairRetirement.parentValue(parent));check(!Pg783ExistingPairRetirement.parentValue(null));
    for(String k:parent.keySet()){var v=new HashMap<>(parent);v.remove(k);check(!Pg783ExistingPairRetirement.parentValue(v));}
    Pg783ExistingPairRetirement.configureSigned();check(Pg387TrustedDeployment.expectedSqlCount==28&&Pg387TrustedDeployment.expectedHistoryCount()==29);
    check(Pg387TrustedDeployment.SOURCE.equals("8d4b68b4f1449932ebe506aaf08e584bbfea8dd2"));
    Pg783ExistingPairRetirement.refsHeld=true;for(String p:List.of("EXISTING_INVALID_PAIR","FIXED_ALL_TERMINAL","PURE_TYPED_RETIRE","REFERENCE_CLOSE"))check(Pg783ExistingPairRetirement.retainRequired(p,false,new Exception("literal")));
    Pg783ExistingPairRetirement.refsHeld=false;check(!Pg783ExistingPairRetirement.retainRequired("BODY",false,new Exception("literal")));
    System.out.println("PG783_JAVA_ORACLE assertions="+count+" independent=true nativeMutation0=true productionPT0=true");
  }
}
