import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
/** PT-OPS-RET462001..003: independent raw launch and expected namespace, no VM actions. */
public final class Pg462TimeoutRetirementTest {
  static int n;
  static void check(boolean v){n++;if(!v)throw new AssertionError("retirement literal "+n);}
  interface Action {void run() throws Exception;}
  static void reject(Action f) throws Exception {n++;try{f.run();throw new AssertionError("foreign launch accepted");}catch(IllegalArgumentException|IllegalStateException|NullPointerException expected){}}
  public static void main(String[] args) throws Exception {
    var expected=new HashSet<>(Pg462TimeoutIsolationTestNames());
    check(expected.size()==21 && expected.equals(Pg462TimeoutRetirement.retiredNames()));
    check(!expected.contains("permit-start.intent") && expected.stream().noneMatch(v->v.endsWith(".start.intent")));
    var run=new BatchRun(UUID.fromString("31100027-2222-4333-8444-555555555555"),Instant.parse("2026-09-27T15:00:00Z"));
    var activation=new MaintenanceActivation(run,UUID.fromString("31100027-6666-4777-8888-999999999999"));
    var e=new StartupPermitRecords.Epoch(StartupPermitRecords.State.ISSUED,UUID.fromString("e07aa706-1acd-4e65-b309-d7f330f79d54"),UUID.fromString("15e4559b-13ab-46d7-a7a8-c15f1de4a245"),activation,Optional.of("1".repeat(64)));
    var owner=new MaintenanceOwnerFrame(e.boot(),run.id(),activation.id(),run.cutoff(),e.epoch(),new MaintenanceOwnerFrame.Parent("a93cd4cdb41a4709af0e976b37389598",628952,9934910),Optional.empty(),100L);
    byte[] ownerBytes="independent-owner-golden".getBytes(StandardCharsets.US_ASCII);
    // Fixed independently calculated SHA256 below, not Production generated expected.
    String ownerHash="bdd85f6dbca445efc0f6ede5e75f5d44576b72ecfa2f9c74a0f72cd2bba7556a";
    String raw="NKLAUNCH1\nservice=API\nboot=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch=15e4559b-13ab-46d7-a7a8-c15f1de4a245\npermit_sha256="+"1".repeat(64)+"\nowner_sha256="+ownerHash+"\ninvocation=bbf96d392f424aa195e8cceb80d02115\npid=771339\nstart_ticks=10008163\n";
    var actual=Pg462TimeoutRetirement.child(raw.getBytes(StandardCharsets.US_ASCII),"API",771339,"bbf96d392f424aa195e8cceb80d02115",10008163,e,owner,"1".repeat(64),ownerBytes);
    check(actual.equals(new MaintenanceOwnerFrame.Parent("bbf96d392f424aa195e8cceb80d02115",771339,10008163)));
    for(String[] change:List.of(new String[]{"service=API","service=WEB"},new String[]{"pid=771339","pid=771340"},new String[]{"start_ticks=10008163","start_ticks=10008164"},new String[]{"bbf96d392f424aa195e8cceb80d02115","0".repeat(32)},new String[]{ownerHash,"2".repeat(64)},new String[]{"NKLAUNCH1","NKLAUNCH2"}))reject(()->Pg462TimeoutRetirement.child(raw.replace(change[0],change[1]).getBytes(StandardCharsets.US_ASCII),"API",771339,"bbf96d392f424aa195e8cceb80d02115",10008163,e,owner,"1".repeat(64),ownerBytes));
    reject(()->Pg462TimeoutRetirement.child(null,"API",771339,"bbf96d392f424aa195e8cceb80d02115",10008163,e,owner,"1".repeat(64),ownerBytes));
    System.out.println("PG462_RETIREMENT_TEST assertions="+n+" independent=true vmMutation=false oldNormalReturnClaimed=false");
  }
  static Set<String> Pg462TimeoutIsolationTestNames(){
    var n=new HashSet<String>();n.add("epoch.current");
    for(String epoch:List.of("1eecb7b9-1e98-478f-9084-201422b31bff","d536cf5a-f5a8-4dd9-8679-3488fab17fdf","e8cce97a-163b-4814-b435-8fc26466e550","25020aa0-7b69-4554-be47-ea69588da569","15e4559b-13ab-46d7-a7a8-c15f1de4a245")){n.add(epoch+".permit");n.add(epoch+".owner");n.add(epoch+".API.launch");n.add(epoch+".WEB.launch");}
    return Set.copyOf(n);
  }
}
