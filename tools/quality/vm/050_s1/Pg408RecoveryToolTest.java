import java.time.*;
import java.util.*;
/** Independent fourteen-column literals; tools only, never counted as Production PT. */
public final class Pg408RecoveryToolTest {
  static int assertions;
  static void check(boolean actual,boolean expected) {
    if(actual!=expected)throw new AssertionError("independent historical row contract");assertions++;
  }
  public static void main(String[] args) {
    for(String status:List.of("SUCCESS","WARNING","FAILED","SKIPPED")) {
      var row=new ArrayList<Object>(Arrays.asList(1L,
          UUID.fromString("31100027-2222-4333-8444-555555555555"),LocalDate.of(2026,9,28),
          "BACKUP_DB",1,OffsetDateTime.parse("2026-09-28T00:00:00Z"),
          OffsetDateTime.parse("2026-09-28T00:00:01Z"),status,1L,0L,1L,0L,null,null));
      check(Pg407FailedRootRecovery.terminalRow(row),true);
      for(int index=0;index<12;index++) {
        var missing=new ArrayList<>(row);missing.set(index,null);
        check(Pg407FailedRootRecovery.terminalRow(missing),false);
      }
      for(String bad:List.of("RUNNING","unknown","")) {
        var wrong=new ArrayList<>(row);wrong.set(7,bad);
        check(Pg407FailedRootRecovery.terminalRow(wrong),false);
      }
      var wrong=new ArrayList<>(row);wrong.set(1,UUID.fromString("41100027-2222-4333-8444-555555555555"));
      check(Pg407FailedRootRecovery.terminalRow(wrong),false);
      check(Pg407FailedRootRecovery.terminalRow(row.subList(0,13)),false);
      wrong=new ArrayList<>(row);wrong.add("extra");check(Pg407FailedRootRecovery.terminalRow(wrong),false);
    }
    check(Pg407FailedRootRecovery.terminalRow(null),false);
    System.out.println("PG408_RECOVERY_TOOL_TEST independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
