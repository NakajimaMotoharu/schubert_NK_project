import java.util.*;
/** Independent literal namespace/argument vectors. Tool tests, ProductionPT0. */
public final class Pg468CodeOnlyDeploymentTest {
  static int n;
  static void check(boolean result){n++;if(!result)throw new AssertionError("code-only vector "+n);}
  public static void main(String[] args) {
    check(Pg468CodeOnlyDeployment.OLD_SOURCE.equals("df9a33febf3703f0d18ac2c4ef56fd0225aac2b9"));
    check(Pg468CodeOnlyDeployment.OLD_DIGEST.equals("8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e"));
    check(Pg468CodeOnlyDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG465"));
    check(Pg468CodeOnlyDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG468"));
    check(Pg468CodeOnlyDeployment.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg468-code-only"));
    String source="df9a33febf3703f0d18ac2c4ef56fd0225aac2b9",digest="1".repeat(64);
    check(Pg468CodeOnlyDeployment.arguments(new String[]{source,digest,"verify"}));
    check(Pg468CodeOnlyDeployment.arguments(new String[]{source,digest,"activate"}));
    check(!Pg468CodeOnlyDeployment.arguments(null));
    check(!Pg468CodeOnlyDeployment.arguments(new String[]{}));
    check(!Pg468CodeOnlyDeployment.arguments(new String[]{source,digest}));
    check(!Pg468CodeOnlyDeployment.arguments(new String[]{source,digest,"activate","extra"}));
    for(String bad:new String[]{"",source.substring(1),source+"0",source.toUpperCase(Locale.ROOT),"g".repeat(40)," "+source})check(!Pg468CodeOnlyDeployment.arguments(new String[]{bad,digest,"verify"}));
    for(String bad:new String[]{"",digest.substring(1),digest+"1","G".repeat(64)," "+digest})check(!Pg468CodeOnlyDeployment.arguments(new String[]{source,bad,"verify"}));
    for(String bad:new String[]{"start","complete","restore","migrate","Activate"," verify",""})check(!Pg468CodeOnlyDeployment.arguments(new String[]{source,digest,bad}));
    for(int i=0;i<3;i++){String[] vector={source,digest,"verify"};vector[i]=null;check(!Pg468CodeOnlyDeployment.arguments(vector));}
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");
    Set<String> fixed=Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch","1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.permit","1ba8ece5-5297-47c3-9933-95b2330beeb0.owner","1ba8ece5-5297-47c3-9933-95b2330beeb0.API.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.WEB.launch","42efb43b-658e-4771-8ad4-b01d658a677b.permit","42efb43b-658e-4771-8ad4-b01d658a677b.owner","42efb43b-658e-4771-8ad4-b01d658a677b.API.launch","42efb43b-658e-4771-8ad4-b01d658a677b.WEB.launch");
    check(Pg468CodeOnlyDeployment.names(fixed,epoch));
    check(fixed.size()==37);
    check(!Pg468CodeOnlyDeployment.names(null,epoch));check(!Pg468CodeOnlyDeployment.names(fixed,null));
    for(String name:fixed){var missing=new HashSet<>(fixed);missing.remove(name);check(!Pg468CodeOnlyDeployment.names(missing,epoch));}
    for(String extra:List.of("foreign","11111111-2222-4333-8444-555555555555.API.start.intent","11111111-2222-4333-8444-555555555555.WEB.start.intent","11111111-2222-4333-8444-555555555555.publication.intent","broker-start.intent")){var plus=new HashSet<>(fixed);plus.add(extra);check(!Pg468CodeOnlyDeployment.names(plus,epoch));}
    var foreign=new HashSet<>(fixed);foreign.remove("11111111-2222-4333-8444-555555555555.owner");foreign.add("22222222-2222-4333-8444-555555555555.owner");check(!Pg468CodeOnlyDeployment.names(foreign,epoch));
    check(!Pg468CodeOnlyDeployment.names(fixed,UUID.fromString("22222222-2222-4333-8444-555555555555")));
    System.out.println("PG468_CODE_ONLY_TOOL_PASS independentAssertions="+n+" productionPt0=true namespaceIntentForeignRejected=true ddlStartsPermitsAbsent=true");
  }
}
