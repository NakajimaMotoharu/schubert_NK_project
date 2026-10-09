import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/** SSC227 independent literal data/CLI, never parent proof or startup authority. */
public final class Pg685CompletedDeploymentTest {
  static MaintenanceRunFiles.StartupOriginal literal(int difference) {
    var run=new BatchRun(UUID.fromString(difference==1 ? "4a53b979-fa01-47dd-92a6-7b26affcfb5c" : "601297d0-a8ba-47da-852b-0ffeae409965"),
      Instant.parse(difference==2 ? "2026-10-08T21:33:23.332579Z" : "2026-10-08T21:33:23.332578Z"));
    var activation=new MaintenanceActivation(run,UUID.fromString(difference==3 ? "870bbce1-6bba-4db0-ace1-680ee7dfde92" : "ad15ac4a-8d8e-4970-bcb3-2e000050ce77"));
    var result=new MaintenanceCompletion(activation,
      Instant.parse(difference==4 ? "2026-10-08T22:03:10.738021Z" : "2026-10-08T22:03:10.738020Z"),
      difference==5 ? MaintenanceCompletion.Outcome.WARNING : MaintenanceCompletion.Outcome.SUCCESS);
    return new MaintenanceRunFiles.StartupOriginal(activation,difference==6 ? Optional.empty() : Optional.of(result));
  }
  public static void main(String[] args) {
    if(!Pg685CompletedDeployment.arguments(new String[]{"verify"}) || !Pg685CompletedDeployment.arguments(new String[]{"activate"}))throw new AssertionError();
    String[][] invalid={null,new String[0],new String[]{null},new String[]{"resume"},new String[]{"activate","foreign"},new String[]{""}};
    for(var value:invalid)if(Pg685CompletedDeployment.arguments(value))throw new AssertionError();
    if(Pg685CompletedDeployment.normalDone(null) || !Pg685CompletedDeployment.normalDone(literal(0)))throw new AssertionError();
    for(int field=1;field<=6;field++)if(Pg685CompletedDeployment.normalDone(literal(field)))throw new AssertionError();
    if(!Pg685CompletedDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG631") || !Pg685CompletedDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG682"))throw new AssertionError();
    if(!Pg685CompletedDeployment.source.equals("9bd50536f692610036a0ed8b83e0a8b35fe2a66f") || !Pg685CompletedDeployment.digest.equals("076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480"))throw new AssertionError();
    System.out.println("PG685_INDEPENDENT_DATA_CLI conditions20=true productionPT0=true");
  }
}
