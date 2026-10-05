import java.util.*;
/** Independent literal namespace/argument vectors. Tool tests, ProductionPT0. */
public final class Pg464CodeOnlyDeploymentTest {
  static int n;
  static void check(boolean result){n++;if(!result)throw new AssertionError("code-only vector "+n);}
  public static void main(String[] args) {
    check(Pg464CodeOnlyDeployment.OLD_SOURCE.equals("11c1feb1c0b51543f98c28e3f54213274648f06f"));
    check(Pg464CodeOnlyDeployment.OLD_DIGEST.equals("0cfd6453948feff4e63912c3169224b0800a0d2c1246f5e06207cab7964386d1"));
    check(Pg464CodeOnlyDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG463"));
    check(Pg464CodeOnlyDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG464"));
    check(Pg464CodeOnlyDeployment.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg464-code-only"));
    String source="11c1feb1c0b51543f98c28e3f54213274648f06f",digest="1".repeat(64);
    check(Pg464CodeOnlyDeployment.arguments(new String[]{source,digest,"verify"}));
    check(Pg464CodeOnlyDeployment.arguments(new String[]{source,digest,"activate"}));
    check(!Pg464CodeOnlyDeployment.arguments(null));
    check(!Pg464CodeOnlyDeployment.arguments(new String[]{}));
    check(!Pg464CodeOnlyDeployment.arguments(new String[]{source,digest}));
    check(!Pg464CodeOnlyDeployment.arguments(new String[]{source,digest,"activate","extra"}));
    for(String bad:new String[]{"",source.substring(1),source+"0",source.toUpperCase(Locale.ROOT),"g".repeat(40)," "+source})check(!Pg464CodeOnlyDeployment.arguments(new String[]{bad,digest,"verify"}));
    for(String bad:new String[]{"",digest.substring(1),digest+"1","G".repeat(64)," "+digest})check(!Pg464CodeOnlyDeployment.arguments(new String[]{source,bad,"verify"}));
    for(String bad:new String[]{"start","complete","restore","migrate","Activate"," verify",""})check(!Pg464CodeOnlyDeployment.arguments(new String[]{source,digest,bad}));
    for(int i=0;i<3;i++){String[] vector={source,digest,"verify"};vector[i]=null;check(!Pg464CodeOnlyDeployment.arguments(vector));}
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");
    Set<String> fixed=Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch","1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch");
    check(Pg464CodeOnlyDeployment.names(fixed,epoch));
    check(fixed.size()==29);
    check(!Pg464CodeOnlyDeployment.names(null,epoch));check(!Pg464CodeOnlyDeployment.names(fixed,null));
    for(String name:fixed){var missing=new HashSet<>(fixed);missing.remove(name);check(!Pg464CodeOnlyDeployment.names(missing,epoch));}
    for(String extra:List.of("foreign","11111111-2222-4333-8444-555555555555.API.start.intent","11111111-2222-4333-8444-555555555555.WEB.start.intent","11111111-2222-4333-8444-555555555555.publication.intent","broker-start.intent")){var plus=new HashSet<>(fixed);plus.add(extra);check(!Pg464CodeOnlyDeployment.names(plus,epoch));}
    var foreign=new HashSet<>(fixed);foreign.remove("11111111-2222-4333-8444-555555555555.owner");foreign.add("22222222-2222-4333-8444-555555555555.owner");check(!Pg464CodeOnlyDeployment.names(foreign,epoch));
    check(!Pg464CodeOnlyDeployment.names(fixed,UUID.fromString("22222222-2222-4333-8444-555555555555")));
    System.out.println("PG464_CODE_ONLY_TOOL_PASS independentAssertions="+n+" productionPt0=true namespaceIntentForeignRejected=true ddlStartsPermitsAbsent=true");
  }
}
