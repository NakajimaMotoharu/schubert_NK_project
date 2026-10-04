import java.util.*;
/** Independent literal namespace/argument vectors. Tool tests, ProductionPT0. */
public final class Pg461CodeOnlyDeploymentTest {
  static int n;
  static void check(boolean result){n++;if(!result)throw new AssertionError("code-only vector "+n);}
  public static void main(String[] args) {
    check(Pg461CodeOnlyDeployment.OLD_SOURCE.equals("8e97eb9138828010926cd47fd10868d8a2d54f11"));
    check(Pg461CodeOnlyDeployment.OLD_DIGEST.equals("88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311"));
    check(Pg461CodeOnlyDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG459"));
    check(Pg461CodeOnlyDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG461"));
    check(Pg461CodeOnlyDeployment.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg461-code-only"));
    String source="8e97eb9138828010926cd47fd10868d8a2d54f11",digest="1".repeat(64);
    check(Pg461CodeOnlyDeployment.arguments(new String[]{source,digest,"verify"}));
    check(Pg461CodeOnlyDeployment.arguments(new String[]{source,digest,"activate"}));
    check(!Pg461CodeOnlyDeployment.arguments(null));
    check(!Pg461CodeOnlyDeployment.arguments(new String[]{}));
    check(!Pg461CodeOnlyDeployment.arguments(new String[]{source,digest}));
    check(!Pg461CodeOnlyDeployment.arguments(new String[]{source,digest,"activate","extra"}));
    for(String bad:new String[]{"",source.substring(1),source+"0",source.toUpperCase(Locale.ROOT),"g".repeat(40)," "+source})check(!Pg461CodeOnlyDeployment.arguments(new String[]{bad,digest,"verify"}));
    for(String bad:new String[]{"",digest.substring(1),digest+"1","G".repeat(64)," "+digest})check(!Pg461CodeOnlyDeployment.arguments(new String[]{source,bad,"verify"}));
    for(String bad:new String[]{"start","complete","restore","migrate","Activate"," verify",""})check(!Pg461CodeOnlyDeployment.arguments(new String[]{source,digest,bad}));
    for(int i=0;i<3;i++){String[] vector={source,digest,"verify"};vector[i]=null;check(!Pg461CodeOnlyDeployment.arguments(vector));}
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");
    Set<String> fixed=Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch","1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch");
    check(Pg461CodeOnlyDeployment.names(fixed,epoch));
    check(fixed.size()==17);
    check(!Pg461CodeOnlyDeployment.names(null,epoch));check(!Pg461CodeOnlyDeployment.names(fixed,null));
    for(String name:fixed){var missing=new HashSet<>(fixed);missing.remove(name);check(!Pg461CodeOnlyDeployment.names(missing,epoch));}
    for(String extra:List.of("foreign","11111111-2222-4333-8444-555555555555.API.start.intent","11111111-2222-4333-8444-555555555555.WEB.start.intent","11111111-2222-4333-8444-555555555555.publication.intent","broker-start.intent")){var plus=new HashSet<>(fixed);plus.add(extra);check(!Pg461CodeOnlyDeployment.names(plus,epoch));}
    var foreign=new HashSet<>(fixed);foreign.remove("11111111-2222-4333-8444-555555555555.owner");foreign.add("22222222-2222-4333-8444-555555555555.owner");check(!Pg461CodeOnlyDeployment.names(foreign,epoch));
    check(!Pg461CodeOnlyDeployment.names(fixed,UUID.fromString("22222222-2222-4333-8444-555555555555")));
    System.out.println("PG461_CODE_ONLY_TOOL_PASS independentAssertions="+n+" productionPt0=true namespaceIntentForeignRejected=true ddlStartsPermitsAbsent=true");
  }
}
