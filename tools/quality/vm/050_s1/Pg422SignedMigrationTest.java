import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Independent preserved public BackupProfile inputs; tool only, never Production PT numerator. */
public final class Pg422SignedMigrationTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=2)throw new IllegalArgumentException("two preserved public profiles");
    byte[] old=Files.readAllBytes(Path.of(args[0])),next=Files.readAllBytes(Path.of(args[1]));
    if(!Pg422SignedMigration.schemaOnly(old,next) || !Pg422SignedMigration.hash(old).equals("cf4da30c449e3fb00ab2e23d308fc6e0b26903d590d3e3f96af0a3d2bb074c55"))throw new AssertionError("independent old profile hash/new-only schema");
    int assertions=2;
    if(Pg422SignedMigration.schemaOnly(old,old) || Pg422SignedMigration.schemaOnly(next,next) || Pg422SignedMigration.schemaOnly(next,old))throw new AssertionError("closed schema23->25");assertions+=3;
    String literal=new String(next,StandardCharsets.US_ASCII);
    for(String[] change:new String[][]{{"ubuntu-26.04","ubuntu-26.05"},{"25.0.4","25.0.5"},{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},{"bb1e1e3a","aa1e1e3a"}}) {
      if(Pg422SignedMigration.schemaOnly(old,literal.replace(change[0],change[1]).getBytes(StandardCharsets.US_ASCII)))throw new AssertionError("other public claim/hash changed");assertions++;
    }
    Pg422SignedMigration.configure();
    if(!Pg387TrustedDeployment.SOURCE.equals("995d3c5386f09b89bc4af4a2e7c9d3fdb9f603e3") || !Pg387TrustedDeployment.RELEASE.equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG421"))
        || !Pg387TrustedDeployment.LABEL.equals("PG421") || !Pg387TrustedDeployment.STEM.equals("pg421") || Pg387TrustedDeployment.expectedHistoryCount()!=26)throw new AssertionError("fixed signedSource/candidate/history");assertions+=5;
    System.out.println("PG422_MIGRATION_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
