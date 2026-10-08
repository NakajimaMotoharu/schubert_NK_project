import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/** SSC227 independent literal data/CLI, never parent proof or startup authority. */
public final class Pg624CompletedDeploymentTest {
  static MaintenanceRunFiles.StartupOriginal literal(int difference) {
    var run=new BatchRun(UUID.fromString(difference==1 ? "4a53b979-fa01-47dd-92a6-7b26affcfb5c" : "3a53b979-fa01-47dd-92a6-7b26affcfb5c"),
      Instant.parse(difference==2 ? "2026-10-08T15:32:46.368376Z" : "2026-10-08T15:32:46.368375Z"));
    var activation=new MaintenanceActivation(run,UUID.fromString(difference==3 ? "870bbce1-6bba-4db0-ace1-680ee7dfde92" : "970bbce1-6bba-4db0-ace1-680ee7dfde92"));
    var result=new MaintenanceCompletion(activation,
      Instant.parse(difference==4 ? "2026-10-08T15:57:38.735147Z" : "2026-10-08T15:57:38.735146Z"),
      difference==5 ? MaintenanceCompletion.Outcome.WARNING : MaintenanceCompletion.Outcome.SUCCESS);
    return new MaintenanceRunFiles.StartupOriginal(activation,difference==6 ? Optional.empty() : Optional.of(result));
  }
  public static void main(String[] args) {
    if(!Pg624CompletedDeployment.arguments(new String[]{"verify"}) || !Pg624CompletedDeployment.arguments(new String[]{"activate"}))throw new AssertionError();
    String[][] invalid={null,new String[0],new String[]{null},new String[]{"resume"},new String[]{"activate","foreign"},new String[]{""}};
    for(var value:invalid)if(Pg624CompletedDeployment.arguments(value))throw new AssertionError();
    if(Pg624CompletedDeployment.normalDone(null) || !Pg624CompletedDeployment.normalDone(literal(0)))throw new AssertionError();
    for(int field=1;field<=6;field++)if(Pg624CompletedDeployment.normalDone(literal(field)))throw new AssertionError();
    if(!Pg624CompletedDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG600") || !Pg624CompletedDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG621"))throw new AssertionError();
    if(!Pg624CompletedDeployment.source.equals("72fb7440697ee1048a5c0145055dc1cc3c577914") || !Pg624CompletedDeployment.digest.equals("4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e"))throw new AssertionError();
    System.out.println("PG624_INDEPENDENT_DATA_CLI conditions20=true productionPT0=true");
  }
}
