import java.io.IOException;
import java.util.*;

/** QA047/SSC174: independent literal failure topology, no private message or path oracle. */
public final class Pg445RecoveryDiagnosticsTest {
  static int count;
  static void check(boolean value){if(!value)throw new AssertionError("fixed redacted diagnosis");count++;}
  static void refused(String tag,Throwable failure) {
    try {Pg428ColdBootPreparation.fixedFailure(tag,failure);throw new AssertionError("invalid diagnosis contract");}
    catch(IllegalArgumentException expected){count++;}
  }
  public static void main(String[] args) {
    Pg428ColdBootPreparation.stage="TRANSFER_TREE";
    var root=new IOException("SECRET_PRIMARY_cookie=value",new IllegalStateException("SECRET_CAUSE_credential"));
    root.addSuppressed(new IOException("SECRET_CLOSE_/private/epoch"));
    String expected="PG431_FIXED_FAILURE stage=TRANSFER_TREE oldOwnerClose=UNKNOWN currentOwnerClose=UNKNOWN diagnosticsRedacted=true\n"
        +"PG431_FAILURE_NODE ordinal=0 edge=PRIMARY type=java.io.IOException knownIo=true secondaryCount=1\n"
        +"PG431_FAILURE_NODE ordinal=1 edge=CAUSE type=java.lang.IllegalStateException knownIo=false secondaryCount=0\n"
        +"PG431_FAILURE_NODE ordinal=2 edge=SECONDARY type=java.io.IOException knownIo=true secondaryCount=0\n";
    String actual=Pg428ColdBootPreparation.fixedFailure("PG431",root);check(expected.equals(actual));
    check(!actual.contains("SECRET") && !actual.contains("credential") && !actual.contains("/private/"));
    check(root.getSuppressed().length==1 && root.getCause() instanceof IllegalStateException);
    refused(null,root);refused("UNKNOWN",root);refused("PG431\nSECRET_INJECTION",root);refused("PG431",null);
    for(String stage:Arrays.asList(null,"unknown","/private/SECRET_PATH","ENTRY\nAuthorization: SECRET")) {
      Pg428ColdBootPreparation.stage=stage;String value=Pg428ColdBootPreparation.fixedFailure("PG428",root);
      check(value.startsWith("PG428_FIXED_FAILURE stage=UNKNOWN_STAGE ") && !value.contains("SECRET"));
    }
    Pg428ColdBootPreparation.stage="PAIR_QUARANTINE";
    var first=new IOException("SECRET_A");var second=new IOException("SECRET_B");
    first.initCause(second);second.initCause(first);first.addSuppressed(second);
    String cycle=Pg428ColdBootPreparation.fixedFailure("PG431",first);
    check(cycle.lines().count()==3 && !cycle.contains("SECRET"));
    var many=new IOException("SECRET_LONG");Throwable head=many;
    for(int i=0;i<40;i++){var next=new IOException("SECRET_"+i);head.initCause(next);head=next;many.addSuppressed(new IllegalArgumentException("SECRET_CLOSE_"+i));}
    String bounded=Pg428ColdBootPreparation.fixedFailure("PG431",many);
    check(bounded.lines().count()==17 && bounded.length()<4096 && !bounded.contains("SECRET"));
    check(bounded.contains("ordinal=0 edge=PRIMARY type=java.io.IOException knownIo=true secondaryCount=40"));
    var unknown=new AssertionError("SECRET_UNKNOWN");
    String failed=Pg428ColdBootPreparation.fixedFailure("PG431",unknown);
    check(failed.contains("edge=PRIMARY type=java.lang.AssertionError knownIo=false secondaryCount=0"));
    check(!failed.contains("SECRET") && failed.contains("currentOwnerClose=UNKNOWN") && !failed.contains("OWNED_CLOSED"));
    System.out.println("PG445_RECOVERY_DIAGNOSTICS success=true independentAssertions="+count+" productionTestCount=0 secretFindings=0");
  }
}
