import java.nio.charset.StandardCharsets;
import java.util.*;

/** MIG202002 pure independent boundary oracle. No DB, guest, permission or Production PT credit. */
public final class Pg490PendingMigrationTest {
  static int checks;
  static void check(boolean value){if(!value)throw new AssertionError("independent migration contract");checks++;}
  static byte[] profile(String schema,String host){
    return ("{\"profile\":\"NKBACKUPPROFILE1\",\"host\":\""+host+"\",\"app\":\"0.1.0-SNAPSHOT\",\"schema\":\""+schema+"\",\"os\":\"ubuntu-26.04\",\"jdk\":\"25.0.4\",\"postgresql\":\"18.6\",\"artemis\":\"2.56.0\",\"age\":\"1.2.1\",\"pgDumpWrapperSha256\":\""+"a".repeat(64)+"\",\"pgRestoreWrapperSha256\":\""+"b".repeat(64)+"\",\"pgDumpSha256\":\""+"c".repeat(64)+"\",\"pgRestoreSha256\":\""+"d".repeat(64)+"\",\"tarSha256\":\""+"e".repeat(64)+"\",\"ageSha256\":\""+"f".repeat(64)+"\",\"artemisArtifactSha256\":\""+"1".repeat(64)+"\"}\n").getBytes(StandardCharsets.US_ASCII);
  }
  public static void main(String[] ignored){
    String source="a".repeat(40),digest="b".repeat(64);
    check(Pg490PendingMigration.arguments(new String[]{source,digest}));
    for(String[] bad:Arrays.asList(null,new String[0],new String[]{source},new String[]{source,digest,"extra"},new String[]{null,digest},new String[]{source,null},new String[]{"x".repeat(40),digest},new String[]{source,"X".repeat(64)},new String[]{"a".repeat(39),digest}))check(!Pg490PendingMigration.arguments(bad));
    byte[] old=profile("027","pgpt-r2"),next=profile("028","pgpt-r2"),held=old.clone();
    check(Pg490PendingMigration.schemaOnly(old,next));check(Arrays.equals(old,held));
    check(!Pg490PendingMigration.schemaOnly(next,old));check(!Pg490PendingMigration.schemaOnly(old,old));
    check(!Pg490PendingMigration.schemaOnly(old,profile("028","changed")));
    check(!Pg490PendingMigration.schemaOnly(profile("026","pgpt-r2"),next));
    check(!Pg490PendingMigration.schemaOnly(null,next));check(!Pg490PendingMigration.schemaOnly(old,null));
    check(Pg490PendingMigration.RUN.toString().equals("91a748b4-1abe-484c-9682-44f46429b324"));
    check(Pg490PendingMigration.CUTOFF.toString().equals("2026-10-06T12:06:14.564793Z"));
    check(Pg490PendingMigration.BUSINESS_ROLES.equals(List.of("schubert_batch","schubert_app","schubert_web_session","schubert_inbox_inspector","schubert_backup")));
    System.out.println("PG490_PURE_ORACLE independentAssertions="+checks+" guestMutations0=true productionPT0=true");
  }
}
