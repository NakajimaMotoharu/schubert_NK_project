import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** REC50 independent literal/hash oracle; tool only, Production PT count zero. */
public final class Pg423AssetFixtureRecoveryTest {
  static int assertions;
  static void expect(boolean expected,Map<String,String> m,Map<String,String> a) {
    if(Pg423AssetFixtureRecovery.known(m,a)!=expected)throw new AssertionError("closed known generation");assertions++;
  }
  static Map<String,String> receipt(boolean morning) {
    var v=new HashMap<String,String>();
    v.put("Id",morning?"schubert-nk-morning-controller.service":"schubert-nk-api.service");
    v.put("LoadState","loaded");v.put("ActiveState",morning?"failed":"inactive");v.put("SubState",morning?"failed":"dead");
    v.put("Job","");v.put("InvocationID",morning?"04a7b1f712284e6693f2e6b6532c5dcb":"7f22eb6b58144e378aa77ff9f856ec4e");
    v.put("Type",morning?"oneshot":"simple");v.put("Restart",morning?"no":"on-failure");v.put("RemainAfterExit","no");
    v.put("MainPID","0");v.put("ControlPID","0");v.put("Result","exit-code");v.put("ExecMainCode","1");v.put("ExecMainStatus",morning?"30":"50");
    v.put("ExecMainStartTimestampMonotonic","100");v.put("ExecMainExitTimestampMonotonic","200");v.put("KillMode","control-group");v.put("SendSIGKILL","no");return v;
  }
  public static void main(String[] args) throws Exception {
    var m=receipt(true);var a=receipt(false);expect(true,m,a);expect(false,null,a);expect(false,m,null);
    for(boolean morning:List.of(false,true)) {
      var base=morning?m:a;
      for(String field:base.keySet()) {
        var missing=new HashMap<>(base);missing.remove(field);expect(false,morning?missing:m,morning?a:missing);
      }
      for(String field:List.of("Id","InvocationID","ExecMainCode","ExecMainStatus","Result","Job","MainPID","ControlPID")) {
        var changed=new HashMap<>(base);changed.put(field,"different");expect(false,morning?changed:m,morning?a:changed);
        changed.put(field,null);expect(false,morning?changed:m,morning?a:changed);
      }
    }
    if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Pg423AssetFixtureRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII)))
        .equals("7d7acfaff4787c3651386cd9a155eba1db2038955544b4e2b0332504096273c6"))throw new AssertionError("independent SQL whole bytes");assertions++;
    if(Pg423AssetFixtureRecovery.NAMES.size()!=19 || !Pg423AssetFixtureRecovery.NAMES.contains("058eaf2b-45ce-410e-b7e0-1c794a246192.API.start.intent")
        || Pg423AssetFixtureRecovery.NAMES.contains("5689f481-b4e3-4d8f-b450-74b980f5c15c.API.start.intent"))throw new AssertionError("independent fixed namespace");assertions++;
    if(args.length==1) {
      byte[] actual=java.nio.file.Files.readAllBytes(java.nio.file.Path.of(args[0]));
      if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual)).equals("853f55345d20148b99f72e212784e152f8c1b63b0c18c2c79129bd8b70956d24"))throw new AssertionError("independent captured watch SHA");
      Pg423AssetFixtureRecovery.watch(actual);assertions++;
    }
    for(String valid:List.of("999 999 999 999","999\t999\t999\t999"," 999   999\t999 999 ")) {
      if(!Pg423AssetFixtureRecovery.fourIds(valid,"999"))throw new AssertionError("actual four numeric ID token form");assertions++;
    }
    for(String invalid:Arrays.asList(null,"","999 999 999","999 999 999 999 999","0 999 999 999","999x 999 999 999")) {
      if(Pg423AssetFixtureRecovery.fourIds(invalid,"999"))throw new AssertionError("closed four numeric ID token form");assertions++;
    }
    byte[] wav=Pg423AssetFixtureRecovery.fixtureBytes();
    if(wav.length!=48 || !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(wav)).equals("114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb"))throw new AssertionError("fixed independent RIFF48 and SHA");assertions++;
    byte[] manifest=Pg423AssetFixtureRecovery.manifestBytes();
    if(!new String(manifest,StandardCharsets.US_ASCII).equals("114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb  audio/pgpt-fixture.wav\n"))throw new AssertionError("independent golden manifest");assertions++;
    try(var channel=java.nio.channels.Channels.newChannel(new java.io.ByteArrayInputStream(manifest))) {
      if(dev.codex.schubert.nk.api.file.AssetChecksumManifest.read(channel,1).entryCount()!=1)throw new AssertionError("independent count1 loader");assertions++;
    }
    byte[] old="key: value\n".getBytes(StandardCharsets.UTF_8);
    if(!new String(Pg423AssetFixtureRecovery.configured(old),StandardCharsets.UTF_8).equals("key: value\n\"nk.api.storage.asset-manifest-entries\": \"1\"\n"))throw new AssertionError("independent YAML append golden");assertions++;
    for(String invalid:List.of("key: value","nk.api.storage.asset-manifest-entries: \"1\"\n")) {
      try {Pg423AssetFixtureRecovery.configured(invalid.getBytes(StandardCharsets.UTF_8));throw new AssertionError("unchanged YAML prerequisites");}
      catch(IllegalStateException expected) {assertions++;}
    }
    System.out.println("PG423_RECOVERY_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}

