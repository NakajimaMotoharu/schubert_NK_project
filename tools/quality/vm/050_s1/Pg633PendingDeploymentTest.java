import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/** SSC228 independent run/CLI literals, no graph observation or VM authority. */
public final class Pg633PendingDeploymentTest {
  static MaintenanceRunFiles.StartupOriginal literal(int difference) {
    var run=new BatchRun(UUID.fromString(difference==1 ? "f49243d5-de84-4714-8612-6912ddc17e9e" : "e49243d5-de84-4714-8612-6912ddc17e9e"),
      Instant.parse(difference==2 ? "2026-10-08T18:32:42.140967Z" : "2026-10-08T18:32:42.140966Z"));
    var activation=new MaintenanceActivation(run,UUID.fromString(difference==3 ? "8d381b67-b37b-48c6-99ac-e04a336f887d" : "7d381b67-b37b-48c6-99ac-e04a336f887d"));
    Optional<MaintenanceCompletion> completed=difference==4 ? Optional.of(new MaintenanceCompletion(activation,
      Instant.parse("2026-10-08T18:33:16.128049Z"), MaintenanceCompletion.Outcome.SUCCESS)) : Optional.empty();
    return new MaintenanceRunFiles.StartupOriginal(activation,completed);
  }
  public static void main(String[] args) {
    if(!Pg633PendingDeployment.arguments(new String[]{"verify"}) || !Pg633PendingDeployment.arguments(new String[]{"activate"}))throw new AssertionError();
    String[][] invalid={null,new String[0],new String[]{null},new String[]{"resume"},new String[]{"activate","foreign"},new String[]{""}};
    for(var value:invalid)if(Pg633PendingDeployment.arguments(value))throw new AssertionError();
    if(Pg633PendingDeployment.pendingOriginal(null) || !Pg633PendingDeployment.pendingOriginal(literal(0)))throw new AssertionError();
    for(int field=1;field<=4;field++)if(Pg633PendingDeployment.pendingOriginal(literal(field)))throw new AssertionError();
    if(!Pg633PendingDeployment.OLD.toString().equals("/opt/schubert-nk/releases/0.1.0-PG621") || !Pg633PendingDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG631"))throw new AssertionError();
    if(!Pg633PendingDeployment.source.equals("36fe7a0b938489d61d17d49c1c30a6fbbef699d5") || !Pg633PendingDeployment.digest.equals("57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe"))throw new AssertionError();
    System.out.println("PG633_INDEPENDENT_DATA_CLI conditions18=true productionPT0=true");
  }
}
