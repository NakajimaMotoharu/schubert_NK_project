import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/** SSC227 independent literal data/CLI, never parent proof or startup authority. */
public final class Pg604CompletedDeploymentTest {
  static MaintenanceRunFiles.StartupOriginal literal(int difference) {
    var run=new BatchRun(UUID.fromString(difference==1 ? "a62b6984-ffc2-4c9d-aea9-e232d9d1ec9e" : "b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e"),
      Instant.parse(difference==2 ? "2026-10-08T07:36:21.802336Z" : "2026-10-08T07:36:21.802335Z"));
    var activation=new MaintenanceActivation(run,UUID.fromString(difference==3 ? "67f0e73d-d334-4882-9284-04246011da54" : "57f0e73d-d334-4882-9284-04246011da54"));
    var result=new MaintenanceCompletion(activation,
      Instant.parse(difference==4 ? "2026-10-08T08:02:11.015743Z" : "2026-10-08T08:02:11.015742Z"),
      difference==5 ? MaintenanceCompletion.Outcome.WARNING : MaintenanceCompletion.Outcome.SUCCESS);
    return new MaintenanceRunFiles.StartupOriginal(activation,difference==6 ? Optional.empty() : Optional.of(result));
  }
  public static void main(String[] args) {
    if(!Pg604CompletedDeployment.arguments(new String[]{"verify"}) || !Pg604CompletedDeployment.arguments(new String[]{"activate"}))throw new AssertionError();
    String[][] invalid={null,new String[0],new String[]{null},new String[]{"resume"},new String[]{"activate","foreign"},new String[]{""}};
    for(var value:invalid)if(Pg604CompletedDeployment.arguments(value))throw new AssertionError();
    if(Pg604CompletedDeployment.normalDone(null) || !Pg604CompletedDeployment.normalDone(literal(0)))throw new AssertionError();
    for(int field=1;field<=6;field++)if(Pg604CompletedDeployment.normalDone(literal(field)))throw new AssertionError();
    if(!Pg604CompletedDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG548") || !Pg604CompletedDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG600"))throw new AssertionError();
    if(!Pg604CompletedDeployment.source.equals("23b14a44b10504172e030bbd6625926bf049fb5c") || !Pg604CompletedDeployment.digest.equals("a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f"))throw new AssertionError();
    System.out.println("PG604_INDEPENDENT_DATA_CLI conditions20=true productionPT0=true");
  }
}
