import java.nio.charset.StandardCharsets;
import java.util.*;

/** Independent literal envelopes/receipt mutations. No native mutation; no Production PT count. */
public final class Pg468Known30PairRecoveryTest {
  static int assertions;
  static void check(boolean value){if(!value)throw new AssertionError("independent timeout recovery vector");assertions++;}
  static byte[] bytes(String s){return s.getBytes(StandardCharsets.US_ASCII);}
  static Map<String,String> receipt(int i){
    var m=new HashMap<String,String>();
    String[] names={"schubert-nk-morning-controller.service","schubert-nk-api.service","schubert-nk-web.service"};
    String[] inv={"86fd86f54b464bd29f73a844ee4f1bd3","28efa4cf44ef4302b4fc9c67d3bb7432","960e8045cf1f4c4b88d7ca0da2fc6f8e"};
    m.put("Id",names[i]);m.put("LoadState","loaded");m.put("ActiveState","failed");m.put("SubState","failed");m.put("Job","");m.put("InvocationID",inv[i]);
    m.put("Type",i==0?"oneshot":"simple");m.put("Restart",i==0?"no":"on-failure");m.put("RemainAfterExit","no");m.put("MainPID","0");m.put("ControlPID","0");
    m.put("Result","exit-code");m.put("ExecMainStartTimestampMonotonic","100000");m.put("ExecMainExitTimestampMonotonic","200000");m.put("ExecMainCode","1");m.put("ExecMainStatus",i==0?"30":"143");m.put("KillMode","control-group");m.put("SendSIGKILL","no");return m;
  }
  public static void main(String[] args){
    if(args.length!=0)throw new IllegalArgumentException("literal only");
    for(int i=0;i<3;i++){
      var valid=receipt(i);check(Pg468Known30PairRecovery.terminal(valid,i));
      for(var entry:Map.of("Result","success","ExecMainStatus","31","MainPID","11","InvocationID","1".repeat(32),"LoadState","not-found","KillMode","process","SendSIGKILL","yes","Type","exec","ExecMainStartTimestampMonotonic","0","ExecMainExitTimestampMonotonic","1").entrySet()){
        var bad=new HashMap<>(valid);bad.put(entry.getKey(),entry.getValue());check(!Pg468Known30PairRecovery.terminal(bad,i));
      }
      for(String k:valid.keySet()) {var missing=new HashMap<>(valid);missing.remove(k);check(!Pg468Known30PairRecovery.terminal(missing,i));var empty=new HashMap<>(valid);empty.put(k,null);check(!Pg468Known30PairRecovery.terminal(empty,i));}
      var unknown=new HashMap<>(valid);unknown.put("unknown","0");check(!Pg468Known30PairRecovery.terminal(unknown,i));
      var malformed=new HashMap<>(valid);malformed.put("ExecMainStartTimestampMonotonic","not-a-number");check(!Pg468Known30PairRecovery.terminal(malformed,i));
    }
    check(!Pg468Known30PairRecovery.terminal(null,0));check(!Pg468Known30PairRecovery.terminal(receipt(0),-1));check(!Pg468Known30PairRecovery.terminal(receipt(0),3));
    String literal="NKLAUNCH1\nservice=API\nboot=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch=31100027-1111-4111-8111-555555555555\npermit_sha256="+"1".repeat(64)+"\nowner_sha256="+"2".repeat(64)+"\ninvocation="+"3".repeat(32)+"\npid=200\nstart_ticks=300\n";
    var expected=Map.of("service","API","boot","e07aa706-1acd-4e65-b309-d7f330f79d54","epoch","31100027-1111-4111-8111-555555555555","permit_sha256","1".repeat(64),"owner_sha256","2".repeat(64),"invocation","3".repeat(32),"pid","200","start_ticks","300");
    check(expected.equals(Pg468Known30PairRecovery.launch(bytes(literal))));
    check(Pg468Known30PairRecovery.launch(bytes(literal.replace("service=API","service=WEB"))).get("service").equals("WEB"));
    for(String bad:List.of(literal.replace("API","CADDY"),literal.replace("pid=200","pid=0200"),literal.replace("start_ticks=300","start_ticks=0"),literal.replace("invocation="+"3".repeat(32),"invocation="+"0".repeat(32)),literal.replace("permit_sha256="+"1".repeat(64),"permit_sha256=unknown"),literal.replace("boot=e07aa706-1acd-4e65-b309-d7f330f79d54","boot=00000000-0000-0000-0000-000000000000"),literal.replace("NKLAUNCH1","NKLAUNCH2"),literal.replace("\n","\r\n"),literal+"\n",literal.substring(0,literal.length()-1),literal.replace("owner_sha256=","permit_sha256="),literal.replace("pid=200","pid=9223372036854775808"))){
      try{Pg468Known30PairRecovery.launch(bytes(bad));throw new AssertionError("bad literal accepted");}catch(IllegalArgumentException|IllegalStateException refused){assertions++;}
    }
    UUID epoch=UUID.fromString("31100027-1111-4111-8111-555555555555");String prefix="31100027-1111-4111-8111-555555555555";
    for(String keep:List.of("epoch.current",prefix+".permit",prefix+".owner",prefix+".API.launch",prefix+".WEB.launch","1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.permit","1ba8ece5-5297-47c3-9933-95b2330beeb0.owner","1ba8ece5-5297-47c3-9933-95b2330beeb0.API.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.WEB.launch","42efb43b-658e-4771-8ad4-b01d658a677b.permit","42efb43b-658e-4771-8ad4-b01d658a677b.owner","42efb43b-658e-4771-8ad4-b01d658a677b.API.launch","42efb43b-658e-4771-8ad4-b01d658a677b.WEB.launch"))check(Pg468Known30PairRecovery.retainedRecord(keep,epoch));
    for(String removed:List.of("permit-start.intent",prefix+".API.start.intent",prefix+".WEB.start.intent",prefix+".CADDY.start.intent","foreign.permit","xpermit-start.intent",prefix+".permit.start.intent"))check(!Pg468Known30PairRecovery.retainedRecord(removed,epoch));
    var actual=new HashSet<>(List.of("epoch.current",prefix+".permit",prefix+".owner",prefix+".API.launch",prefix+".WEB.launch",prefix+".API.start.intent",prefix+".WEB.start.intent","permit-start.intent"));
    actual.addAll(List.of("1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.permit","1ba8ece5-5297-47c3-9933-95b2330beeb0.owner","1ba8ece5-5297-47c3-9933-95b2330beeb0.API.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.WEB.launch","42efb43b-658e-4771-8ad4-b01d658a677b.permit","42efb43b-658e-4771-8ad4-b01d658a677b.owner","42efb43b-658e-4771-8ad4-b01d658a677b.API.launch","42efb43b-658e-4771-8ad4-b01d658a677b.WEB.launch"));
    String[] reverse={prefix+".WEB.start.intent",prefix+".API.start.intent","permit-start.intent"};
    for(int step=0;step<=3;step++){
      check(Pg468Known30PairRecovery.retirementStage(actual,epoch,step)==step);
      for(String old:List.of("1eecb7b9-1e98-478f-9084-201422b31bff.permit","1eecb7b9-1e98-478f-9084-201422b31bff.owner","1eecb7b9-1e98-478f-9084-201422b31bff.API.launch","1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.permit","1ba8ece5-5297-47c3-9933-95b2330beeb0.owner","1ba8ece5-5297-47c3-9933-95b2330beeb0.API.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.WEB.launch","42efb43b-658e-4771-8ad4-b01d658a677b.permit","42efb43b-658e-4771-8ad4-b01d658a677b.owner","42efb43b-658e-4771-8ad4-b01d658a677b.API.launch","42efb43b-658e-4771-8ad4-b01d658a677b.WEB.launch")) {
        var erased=new HashSet<>(actual);erased.remove(old);try{Pg468Known30PairRecovery.retirementStage(erased,epoch,step);throw new AssertionError("retained prior erased");}catch(IllegalStateException refused){assertions++;}
      }
      if(step>0)check(Pg468Known30PairRecovery.retirementStage(actual,epoch,step-1)==step);
      for(String foreign:List.of("foreign.part","41100027-1111-4111-8111-555555555555.permit","41100027-1111-4111-8111-555555555555.owner",prefix+".CADDY.start.intent")){
        var changed=new HashSet<>(actual);changed.add(foreign);try{Pg468Known30PairRecovery.retirementStage(changed,epoch,step);throw new AssertionError("foreign phase accepted");}catch(IllegalStateException refused){assertions++;}
      }
      if(step>0){var backward=new HashSet<>(actual);backward.add(reverse[step-1]);try{Pg468Known30PairRecovery.retirementStage(backward,epoch,step);throw new AssertionError("backward phase accepted");}catch(IllegalStateException refused){assertions++;}}
      if(step<2){var jump=new HashSet<>(actual);jump.remove(reverse[step]);jump.remove(reverse[step+1]);try{Pg468Known30PairRecovery.retirementStage(jump,epoch,step);throw new AssertionError("jump accepted");}catch(IllegalStateException refused){assertions++;}}
      if(step<3)actual.remove(reverse[step]);
    }
    check(actual.size()==37 && Pg468Known30PairRecovery.fullyRetired(actual,epoch));
    for(String record:actual){var missing=new HashSet<>(actual);missing.remove(record);check(!Pg468Known30PairRecovery.fullyRetired(missing,epoch));}
    for(String extra:List.of("permit-start.intent",prefix+".API.start.intent",prefix+".WEB.start.intent","unknown.part")){var changed=new HashSet<>(actual);changed.add(extra);check(!Pg468Known30PairRecovery.fullyRetired(changed,epoch));}
    for(Throwable secondary:List.of(new java.io.IOException("synthetic IO"),new IllegalStateException("synthetic Runtime"),new AssertionError("synthetic Error"))){
      var primary=new java.io.IOException("same primary");int[] calls={0};Pg468Known30PairRecovery.quarantineAfterUnknown(primary,()->{calls[0]++;if(secondary instanceof Error e)throw e;throw (Exception)secondary;});
      check(calls[0]==1 && primary.getSuppressed().length==1 && primary.getSuppressed()[0]==secondary);
    }
    var primary=new java.io.IOException("same primary");int[] calls={0};Pg468Known30PairRecovery.quarantineAfterUnknown(primary,()->{calls[0]++;return Boolean.TRUE;});check(calls[0]==1 && primary.getSuppressed().length==0);
    Pg468Known30PairRecovery.quarantineAfterUnknown(primary,()->{throw primary;});check(primary.getSuppressed().length==0);
    for(Throwable admission:List.of(new java.io.IOException("post verify"),new IllegalStateException("A close"),new AssertionError("post A Error"))) {
      int[] restores={0};check(Pg468Known30PairRecovery.afterAdmissionFailure(admission,true,()->{restores[0]++;return Boolean.TRUE;}));check(restores[0]==1 && admission.getSuppressed().length==0);
    }
    var beforeAdmission=new java.io.IOException("before mutation");int[] restores={0};check(!Pg468Known30PairRecovery.afterAdmissionFailure(beforeAdmission,false,()->{restores[0]++;return Boolean.TRUE;}));check(restores[0]==0);
    var failedRestore=new java.io.IOException("post A");check(Pg468Known30PairRecovery.afterAdmissionFailure(failedRestore,true,()->{throw new java.io.IOException("A unavailable");}));check(failedRestore.getSuppressed().length==1);
    var suppressedClose=new java.io.IOException("primary");suppressedClose.addSuppressed(new java.io.IOException("owned close"));check(Pg468Known30PairRecovery.afterAdmissionFailure(suppressedClose,false,()->{throw new AssertionError("must not restore before mutation");}));
    System.out.println("PG468_TIMEOUT_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
