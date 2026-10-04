/** SSC178 tool-only explicit schema expectations; never DB/BOM-derived or Production PT credit. */
public final class Pg455ReleaseSchemaToolTest {
  public static void main(String[] args) {
    if(args.length!=0)throw new IllegalArgumentException("fixed test only");
    String label=Pg387TrustedDeployment.LABEL,source=Pg387TrustedDeployment.SOURCE;
    int sql=Pg387TrustedDeployment.expectedSqlCount;
    int assertions=0;
    try {
      for(String schema:new String[]{"025","027"}) {
        Pg387TrustedDeployment.expectedSchema(schema);
        for(String candidate:new String[]{"PG430","PG455"}) {
          Pg387TrustedDeployment.LABEL=candidate;Pg387TrustedDeployment.SOURCE="a".repeat(40);
          int expected=schema.equals("027")?28:26;
          if(Pg387TrustedDeployment.expectedHistoryCount()!=expected)throw new AssertionError("independent fixed count");
          assertions++;
        }
      }
      Pg387TrustedDeployment.LABEL="PG408";
      Pg387TrustedDeployment.SOURCE="32c6a7b1e79abf114901003c4a8f1300b33bf0c0";
      Pg387TrustedDeployment.expectedSchema("025");
      if(Pg387TrustedDeployment.expectedHistoryCount()!=24)throw new AssertionError("legacy preservation count"); assertions++;
      Pg387TrustedDeployment.expectedSchema("027");
      if(Pg387TrustedDeployment.expectedHistoryCount()!=28)throw new AssertionError("explicit027 cannot borrow old23 count"); assertions++;
      for(String bad:new String[]{"", "026", "028", "27", "SCHEMA027"}) {
        int before=Pg387TrustedDeployment.expectedSqlCount;
        try {Pg387TrustedDeployment.expectedSchema(bad);throw new AssertionError("unapproved count accepted");}
        catch(IllegalArgumentException expected) {if(before!=Pg387TrustedDeployment.expectedSqlCount)throw new AssertionError("rejection mutated expectation");}
        assertions++;
      }
      System.out.println("PG455_SCHEMA_TOOL_PASS assertions="+assertions+" productionPtCount=0 observedCountsUsed=false");
    } finally {
      Pg387TrustedDeployment.LABEL=label;Pg387TrustedDeployment.SOURCE=source;Pg387TrustedDeployment.expectedSqlCount=sql;
    }
  }
}
