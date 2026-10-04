import java.util.*;
import java.nio.charset.StandardCharsets;
/** Actual PG458 Root/ordinary evidence; no authority from reconstructed actors. */
public final class Pg459CapturedPeers {
  static final String SOURCE="ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a";
  static final String API="386729898874494ebff10f86647d3e3a",WEB="5b8cd47d114d465582216725317d6788";
  static void require(boolean b){if(!b)throw new IllegalStateException("actual peer capture differs");}
  static void watch(byte[] raw) {
    boolean apiRoot=false,apiOrdinary=false,webRoot=false,webOrdinary=false,apiReady=false,webReady=false;
    for(String line:new String(raw,StandardCharsets.UTF_8).split("\n")) {
      var v=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
      if(v.has("ready")) {
        if(!Set.of("api","web").contains(v.get("ready").getAsString()) || !v.get("sameRootOrdinary").getAsBoolean()
            || !v.get("sameParent").getAsBoolean() || !v.get("ownedSocket").getAsBoolean()
            || !com.google.gson.JsonParser.parseString("{\"commit\":\""+SOURCE+"\",\"app\":\"0.1.0-SNAPSHOT\",\"config\":\"1\",\"schema\":\"027\",\"protocol\":\"0.1.0-SNAPSHOT\"}").equals(v.get("info")))throw new IllegalStateException("actual same-peer ready required");if(v.get("ready").getAsString().equals("api"))apiReady=true;else webReady=true;
      }
      if(!v.has("states"))continue;
      var parent=v.getAsJsonObject("states").getAsJsonObject("morning");
      if(parent.has("entry"))require(parent.get("InvocationID").getAsString().equals("fb3eaf763a8c4a5e8172d3c42f8fc954") && parent.get("MainPID").getAsString().equals("162624") && parent.get("startTicks").getAsLong()==8411500);
      for(String role:List.of("api","web")) {
        var a=v.getAsJsonObject("states").getAsJsonObject(role);if(!a.has("entry"))continue;
        boolean api=role.equals("api");
        if(!a.get("MainPID").getAsString().equals(api?"304687":"306804") || !a.get("InvocationID").getAsString().equals(api?API:WEB)
            || a.get("startTicks").getAsLong()!=(api?8483207:8484334))throw new IllegalStateException("same captured child required");
        String entry=a.get("entry").getAsString();
        var process=a.getAsJsonObject("process");
        if(process==null || !process.keySet().equals(Set.of("Uid","Gid","Groups","NoNewPrivs","CapInh","CapPrm","CapEff","CapBnd","CapAmb")))throw new IllegalStateException("closed process fields required");
        if(entry.equals("dev.codex.schubert.nk.batch.file.RootServiceLauncher")) {
          if(!Pg425KnownApiRecovery.fourIds(process.get("Uid").getAsString(),"0"))throw new IllegalStateException("actual Root entry required");
          if(api)apiRoot=true;else webRoot=true;
        }
        if(entry.equals("dev.codex.schubert.nk."+role+".bootstrap."+(api?"Api":"Web")+"ProcessMain")) {
          var p=a.getAsJsonObject("process");
          if(!Pg425KnownApiRecovery.fourIds(p.get("Uid").getAsString(),api?"999":"997")
              || !Pg425KnownApiRecovery.fourIds(p.get("Gid").getAsString(),api?"981":"980")
              || !p.get("Groups").getAsString().equals(api?"980 981 982 986":"980 982 986")
              || !p.get("NoNewPrivs").getAsString().equals("1"))throw new IllegalStateException("fixed ordinary identity required");
          for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))if(!p.get(cap).getAsString().equals("0000000000000000"))throw new IllegalStateException("capability drift");
          if(api)apiOrdinary=true;else webOrdinary=true;
        }
      }
    }
    if(!apiRoot || !apiOrdinary || !webRoot || !webOrdinary || !apiReady || !webReady)throw new IllegalStateException("genuine complete pair observation required");
  }
}
