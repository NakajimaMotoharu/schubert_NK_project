import java.util.*;
/** Independent literal namespace/argument vectors. Tool tests, ProductionPT0. */
public final class Pg459CodeOnlyDeploymentTest {
  static int n;
  static void check(boolean result){n++;if(!result)throw new AssertionError("code-only vector "+n);}
  public static void main(String[] args) {
    String source="8e97eb9138828010926cd47fd10868d8a2d54f11",digest="1".repeat(64);
    check(Pg459CodeOnlyDeployment.arguments(new String[]{source,digest,"verify"}));
    check(Pg459CodeOnlyDeployment.arguments(new String[]{source,digest,"activate"}));
    check(!Pg459CodeOnlyDeployment.arguments(null));
    check(!Pg459CodeOnlyDeployment.arguments(new String[]{}));
    check(!Pg459CodeOnlyDeployment.arguments(new String[]{source,digest}));
    check(!Pg459CodeOnlyDeployment.arguments(new String[]{source,digest,"activate","extra"}));
    for(String bad:new String[]{"",source.substring(1),source+"0",source.toUpperCase(Locale.ROOT),"g".repeat(40)," "+source})check(!Pg459CodeOnlyDeployment.arguments(new String[]{bad,digest,"verify"}));
    for(String bad:new String[]{"",digest.substring(1),digest+"1","G".repeat(64)," "+digest})check(!Pg459CodeOnlyDeployment.arguments(new String[]{source,bad,"verify"}));
    for(String bad:new String[]{"start","complete","restore","migrate","Activate"," verify",""})check(!Pg459CodeOnlyDeployment.arguments(new String[]{source,digest,bad}));
    for(int i=0;i<3;i++){String[] vector={source,digest,"verify"};vector[i]=null;check(!Pg459CodeOnlyDeployment.arguments(vector));}
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");
    Set<String> fixed=Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch","1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch");
    check(Pg459CodeOnlyDeployment.names(fixed,epoch));
    check(!Pg459CodeOnlyDeployment.names(null,epoch));check(!Pg459CodeOnlyDeployment.names(fixed,null));
    for(String name:fixed){var missing=new HashSet<>(fixed);missing.remove(name);check(!Pg459CodeOnlyDeployment.names(missing,epoch));}
    for(String extra:List.of("foreign","11111111-2222-4333-8444-555555555555.API.start.intent","11111111-2222-4333-8444-555555555555.WEB.start.intent","11111111-2222-4333-8444-555555555555.publication.intent","broker-start.intent")){var plus=new HashSet<>(fixed);plus.add(extra);check(!Pg459CodeOnlyDeployment.names(plus,epoch));}
    var foreign=new HashSet<>(fixed);foreign.remove("11111111-2222-4333-8444-555555555555.owner");foreign.add("22222222-2222-4333-8444-555555555555.owner");check(!Pg459CodeOnlyDeployment.names(foreign,epoch));
    check(!Pg459CodeOnlyDeployment.names(fixed,UUID.fromString("22222222-2222-4333-8444-555555555555")));
    System.out.println("PG459_CODE_ONLY_TOOL_PASS independentAssertions="+n+" productionPt0=true namespaceIntentForeignRejected=true ddlStartsPermitsAbsent=true");
  }
}
