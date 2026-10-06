import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;

/** Literal source/DONE/metadata-order/UNKNOWN vectors. Tool assertions only, Production PT0. */
public final class Pg477StoppedDeploymentTest {
  static int checks;
  static void check(boolean value){checks++;if(!value)throw new AssertionError("stopped vector "+checks);}
  static MaintenanceRunFiles.StartupOriginal original(UUID run,UUID activation,String ended,MaintenanceCompletion.Outcome outcome){
    var value=new MaintenanceActivation(new BatchRun(run,Instant.parse("2026-09-27T15:00:00Z")),activation);
    return new MaintenanceRunFiles.StartupOriginal(value,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(value,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args){
    check(Pg477StoppedDeployment.SOURCE.equals("cce61f63900b1479f9f8dbdc338e222b1c8c38a3"));
    check(Pg477StoppedDeployment.DIGEST.equals("613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667"));
    check(Pg477StoppedDeployment.OLD_SOURCE.equals("979c5ac3e9c28ae76363adacdf9f0736f5a59df1"));
    for(String action:List.of("verify","activate"))check(Pg477StoppedDeployment.arguments(new String[]{action}));
    check(!Pg477StoppedDeployment.arguments(null));check(!Pg477StoppedDeployment.arguments(new String[0]));
    check(!Pg477StoppedDeployment.arguments(new String[]{null}));check(!Pg477StoppedDeployment.arguments(new String[]{"verify","extra"}));
    for(String action:List.of("","stop","start","restore","migrate","Activate"," verify"))check(!Pg477StoppedDeployment.arguments(new String[]{action}));
    UUID run=UUID.fromString("31100027-2222-4333-8444-555555555555"),activation=UUID.fromString("33333333-2222-4333-8444-555555555555"),foreign=UUID.fromString("44444444-2222-4333-8444-555555555555");
    check(!Pg477StoppedDeployment.normalDone(null));
    check(!Pg477StoppedDeployment.normalDone(original(run,activation,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-06T03:26:09Z","2026-10-06T03:49:00Z","2026-10-06T03:56:10Z"))check(Pg477StoppedDeployment.normalDone(original(run,activation,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-06T03:26:08.999999Z","2026-10-06T03:56:10.000001Z"))check(!Pg477StoppedDeployment.normalDone(original(run,activation,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(var outcome:MaintenanceCompletion.Outcome.values())check(Pg477StoppedDeployment.normalDone(original(run,activation,"2026-10-06T03:49:00Z",outcome))==(outcome==MaintenanceCompletion.Outcome.SUCCESS));
    check(!Pg477StoppedDeployment.normalDone(original(foreign,activation,"2026-10-06T03:49:00Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg477StoppedDeployment.normalDone(original(run,UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7"),"2026-10-06T03:49:00Z",MaintenanceCompletion.Outcome.SUCCESS)));
    var actual=Map.<String,Map<String,Object>>of("epoch.current",Map.of("uid",0,"mode",33152,"ino",42L),"literal.permit",Map.of("size",123L,"gid",0));
    String first="{epoch.current={uid=0, mode=33152, ino=42}, literal.permit={size=123, gid=0}}";
    String reordered="{literal.permit={gid=0, size=123}, epoch.current={ino=42, mode=33152, uid=0}}";
    check(Pg477StoppedDeployment.sameMetadata(actual,first));check(Pg477StoppedDeployment.sameMetadata(actual,reordered));
    check(!Pg477StoppedDeployment.sameMetadata(null,first));check(!Pg477StoppedDeployment.sameMetadata(actual,null));
    check(!Pg477StoppedDeployment.sameMetadata(actual,"{}"));
    check(!Pg477StoppedDeployment.sameMetadata(actual,first.replace("ino=42","ino=43")));
    check(!Pg477StoppedDeployment.sameMetadata(actual,first.replace("mode=33152","mode=33153")));
    check(!Pg477StoppedDeployment.sameMetadata(actual,first.replace("literal.permit","foreign.permit")));
    for(String stage:new String[]{null,"PREFLIGHT","BODY","STOPPED_HELPER_READBACK","SIGNED_OLD","REFERENCE_SCOPE_CLOSE","DATABASE_SCOPE_CLOSE","A_SCOPE_CLOSE","M_SCOPE_CLOSE"}){
      var ordinary=new IllegalStateException("synthetic");var secondary=new IllegalStateException("synthetic");secondary.addSuppressed(new java.io.IOException("synthetic"));
      for(boolean changed:new boolean[]{false,true})for(Throwable failure:new Throwable[]{ordinary,secondary,new AssertionError("synthetic")})
        check(Pg477StoppedDeployment.retainRequired(stage,changed,failure)==(changed || (stage!=null && (stage.endsWith("_SCOPE_CLOSE") || failure instanceof Error || failure.getSuppressed().length>0))));
    }
    String inspector="[Unit]\nDescription=literal\n[Service]\nExecStart=/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector\n";
    String bootstrap="[Unit]\nDescription=literal\n[Service]\nExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -cp literal BootstrapAdminMain\n";
    String ip="systemd/schubert-nk-inbox-inspector.service",bp="systemd/schubert-nk-bootstrap-admin.service";
    var ascii=java.nio.charset.StandardCharsets.US_ASCII;
    byte[] ia=(inspector+"\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-inspector196\n").getBytes(ascii);
    byte[] ba=("[Unit]\nDescription=literal\n[Service]\nExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary -cp literal BootstrapAdminMain\n\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-bootstrap196\n").getBytes(ascii);
    check(Pg477StoppedDeployment.allowedUnitDelta(ip,inspector.getBytes(ascii),ia));
    check(Pg477StoppedDeployment.allowedUnitDelta(bp,bootstrap.getBytes(ascii),ba));
    check(Pg477StoppedDeployment.allowedUnitDelta("config/literal",ia,ia.clone()));
    for(String name:List.of(ip,bp,"systemd/schubert-nk-api.service")) {
      check(!Pg477StoppedDeployment.allowedUnitDelta(name,inspector.getBytes(ascii),ba));
      check(!Pg477StoppedDeployment.allowedUnitDelta(name,null,ia));
      check(!Pg477StoppedDeployment.allowedUnitDelta(name,new byte[0],ia));
      check(!Pg477StoppedDeployment.allowedUnitDelta(name,new byte[65537],ia));
    }
    check(!Pg477StoppedDeployment.allowedUnitDelta(ip,inspector.getBytes(ascii),(new String(ia,ascii)+"Environment=FOREIGN=1\n").getBytes(ascii)));
    check(!Pg477StoppedDeployment.allowedUnitDelta(bp,bootstrap.getBytes(ascii),new String(ba,ascii).replace("BOOTSTRAP-","API-").getBytes(ascii)));
    check(!Pg477StoppedDeployment.allowedUnitDelta(null,ia,ia));
    var utf8=java.nio.charset.StandardCharsets.UTF_8;
    check(Pg477StoppedDeployment.allowedUnitDelta(ip,("# SS343§8.2\n"+inspector).getBytes(utf8),("# SS343§8.2\n"+new String(ia,ascii)).getBytes(utf8)));
    check(Pg477StoppedDeployment.allowedUnitDelta(bp,("# SS343§8.2\n"+bootstrap).getBytes(utf8),("# SS343§8.2\n"+new String(ba,ascii)).getBytes(utf8)));
    check(!Pg477StoppedDeployment.allowedUnitDelta(bp,new byte[]{(byte)0xc3,10},ba));
    for(char control:new char[]{0,1,13,127})check(!Pg477StoppedDeployment.allowedUnitDelta(ip,(control+inspector).getBytes(utf8),ia));
    for(String name:List.of("REF_READY","REF_CHECKED","REF_CONFIGURED","REF_RELEASED")) {
      check(Pg477UnitReferences.reply(name,(name+"\n").getBytes(ascii)));
      check(!Pg477UnitReferences.reply(name,name.getBytes(ascii)));
      check(!Pg477UnitReferences.reply(name,(name+"\r\n").getBytes(ascii)));
      check(!Pg477UnitReferences.reply(name,(name+"\nREF_FAILED\n").getBytes(ascii)));
      check(!Pg477UnitReferences.reply(name,null));
      check(!Pg477UnitReferences.reply(name,new byte[65]));
    }
    check(!Pg477UnitReferences.reply(null,new byte[0]));
    check(!Pg477UnitReferences.reply("REF_FAILED","REF_FAILED\n".getBytes(ascii)));
    check(!Pg477UnitReferences.reply("REF_READY\nREF_RELEASED","REF_READY\nREF_RELEASED\n".getBytes(ascii)));
    System.out.println("PG477_STOPPED_TEST independentAssertions="+checks+" mutation0=true productionPT0=true");
  }
}
