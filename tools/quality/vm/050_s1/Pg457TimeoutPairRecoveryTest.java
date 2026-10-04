import java.nio.charset.StandardCharsets;
import java.util.*;

/** Independent literal envelopes/receipt mutations. No native mutation; no Production PT count. */
public final class Pg457TimeoutPairRecoveryTest {
  static int assertions;
  static void check(boolean value){if(!value)throw new AssertionError("independent timeout recovery vector");assertions++;}
  static byte[] bytes(String s){return s.getBytes(StandardCharsets.US_ASCII);}
  static Map<String,String> receipt(int i){
    var m=new HashMap<String,String>();
    String[] names={"schubert-nk-morning-controller.service","schubert-nk-api.service","schubert-nk-web.service"};
    String[] inv={"0735b37478204b49a5b2810c882ee3be","0f254ac7a80844afb0fef3c8654cb5ab","8c9f2c9605034ed78b0ed2a7c0e5f93e"};
    m.put("Id",names[i]);m.put("LoadState","loaded");m.put("ActiveState","failed");m.put("SubState","failed");m.put("Job","");m.put("InvocationID",inv[i]);
    m.put("Type",i==0?"oneshot":"simple");m.put("Restart",i==0?"no":"on-failure");m.put("RemainAfterExit","no");m.put("MainPID","0");m.put("ControlPID","0");
    m.put("Result",i==0?"timeout":"exit-code");m.put("ExecMainStartTimestampMonotonic","100000");m.put("ExecMainExitTimestampMonotonic","200000");m.put("ExecMainCode","1");m.put("ExecMainStatus","143");m.put("KillMode","control-group");m.put("SendSIGKILL","no");return m;
  }
  public static void main(String[] args){
    if(args.length!=0)throw new IllegalArgumentException("literal only");
    for(int i=0;i<3;i++){
      var valid=receipt(i);check(Pg457TimeoutPairRecovery.terminal(valid,i));
      for(var entry:Map.of("Result","success","ExecMainStatus","30","MainPID","11","InvocationID","1".repeat(32),"LoadState","not-found","KillMode","process","SendSIGKILL","yes","Type","exec","ExecMainStartTimestampMonotonic","0","ExecMainExitTimestampMonotonic","1").entrySet()){
        var bad=new HashMap<>(valid);bad.put(entry.getKey(),entry.getValue());check(!Pg457TimeoutPairRecovery.terminal(bad,i));
      }
      for(String k:valid.keySet()) {var missing=new HashMap<>(valid);missing.remove(k);check(!Pg457TimeoutPairRecovery.terminal(missing,i));var empty=new HashMap<>(valid);empty.put(k,null);check(!Pg457TimeoutPairRecovery.terminal(empty,i));}
      var unknown=new HashMap<>(valid);unknown.put("unknown","0");check(!Pg457TimeoutPairRecovery.terminal(unknown,i));
      var malformed=new HashMap<>(valid);malformed.put("ExecMainStartTimestampMonotonic","not-a-number");check(!Pg457TimeoutPairRecovery.terminal(malformed,i));
    }
    check(!Pg457TimeoutPairRecovery.terminal(null,0));check(!Pg457TimeoutPairRecovery.terminal(receipt(0),-1));check(!Pg457TimeoutPairRecovery.terminal(receipt(0),3));
    String literal="NKLAUNCH1\nservice=API\nboot=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch=31100027-1111-4111-8111-555555555555\npermit_sha256="+"1".repeat(64)+"\nowner_sha256="+"2".repeat(64)+"\ninvocation="+"3".repeat(32)+"\npid=200\nstart_ticks=300\n";
    var expected=Map.of("service","API","boot","e07aa706-1acd-4e65-b309-d7f330f79d54","epoch","31100027-1111-4111-8111-555555555555","permit_sha256","1".repeat(64),"owner_sha256","2".repeat(64),"invocation","3".repeat(32),"pid","200","start_ticks","300");
    check(expected.equals(Pg457TimeoutPairRecovery.launch(bytes(literal))));
    check(Pg457TimeoutPairRecovery.launch(bytes(literal.replace("service=API","service=WEB"))).get("service").equals("WEB"));
    for(String bad:List.of(literal.replace("API","CADDY"),literal.replace("pid=200","pid=0200"),literal.replace("start_ticks=300","start_ticks=0"),literal.replace("invocation="+"3".repeat(32),"invocation="+"0".repeat(32)),literal.replace("permit_sha256="+"1".repeat(64),"permit_sha256=unknown"),literal.replace("boot=e07aa706-1acd-4e65-b309-d7f330f79d54","boot=00000000-0000-0000-0000-000000000000"),literal.replace("NKLAUNCH1","NKLAUNCH2"),literal.replace("\n","\r\n"),literal+"\n",literal.substring(0,literal.length()-1),literal.replace("owner_sha256=","permit_sha256="),literal.replace("pid=200","pid=9223372036854775808"))){
      try{Pg457TimeoutPairRecovery.launch(bytes(bad));throw new AssertionError("bad literal accepted");}catch(IllegalArgumentException|IllegalStateException refused){assertions++;}
    }
    UUID epoch=UUID.fromString("31100027-1111-4111-8111-555555555555");String prefix="31100027-1111-4111-8111-555555555555";
    var actual=new HashSet<>(List.of("epoch.current",prefix+".permit",prefix+".owner",prefix+".API.launch",prefix+".WEB.launch",prefix+".API.start.intent",prefix+".WEB.start.intent","permit-start.intent"));
    String[] reverse={prefix+".WEB.start.intent",prefix+".API.start.intent","permit-start.intent"};
    for(int step=0;step<=3;step++){
      check(Pg457TimeoutPairRecovery.retirementStage(actual,epoch,step)==step);
      if(step>0)check(Pg457TimeoutPairRecovery.retirementStage(actual,epoch,step-1)==step);
      for(String foreign:List.of("foreign.part","41100027-1111-4111-8111-555555555555.permit","41100027-1111-4111-8111-555555555555.owner",prefix+".CADDY.start.intent")){
        var changed=new HashSet<>(actual);changed.add(foreign);try{Pg457TimeoutPairRecovery.retirementStage(changed,epoch,step);throw new AssertionError("foreign phase accepted");}catch(IllegalStateException refused){assertions++;}
      }
      if(step>0){var backward=new HashSet<>(actual);backward.add(reverse[step-1]);try{Pg457TimeoutPairRecovery.retirementStage(backward,epoch,step);throw new AssertionError("backward phase accepted");}catch(IllegalStateException refused){assertions++;}}
      if(step<2){var jump=new HashSet<>(actual);jump.remove(reverse[step]);jump.remove(reverse[step+1]);try{Pg457TimeoutPairRecovery.retirementStage(jump,epoch,step);throw new AssertionError("jump accepted");}catch(IllegalStateException refused){assertions++;}}
      if(step<3)actual.remove(reverse[step]);
    }
    for(Throwable secondary:List.of(new java.io.IOException("synthetic IO"),new IllegalStateException("synthetic Runtime"),new AssertionError("synthetic Error"))){
      var primary=new java.io.IOException("same primary");int[] calls={0};Pg457TimeoutPairRecovery.quarantineAfterUnknown(primary,()->{calls[0]++;if(secondary instanceof Error e)throw e;throw (Exception)secondary;});
      check(calls[0]==1 && primary.getSuppressed().length==1 && primary.getSuppressed()[0]==secondary);
    }
    var primary=new java.io.IOException("same primary");int[] calls={0};Pg457TimeoutPairRecovery.quarantineAfterUnknown(primary,()->{calls[0]++;return Boolean.TRUE;});check(calls[0]==1 && primary.getSuppressed().length==0);
    Pg457TimeoutPairRecovery.quarantineAfterUnknown(primary,()->{throw primary;});check(primary.getSuppressed().length==0);
    System.out.println("PG457_TIMEOUT_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
