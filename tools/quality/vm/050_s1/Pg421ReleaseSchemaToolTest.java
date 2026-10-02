/** Tool-only independent closed migration expectations; not a Production PT numerator. */
public final class Pg421ReleaseSchemaToolTest {
  public static void main(String[] arguments) {
    String oldLabel=Pg387TrustedDeployment.LABEL, oldSource=Pg387TrustedDeployment.SOURCE;
    try {
      Pg387TrustedDeployment.LABEL="PG408";
      Pg387TrustedDeployment.SOURCE="32c6a7b1e79abf114901003c4a8f1300b33bf0c0";
      if(Pg387TrustedDeployment.expectedHistoryCount()!=24)throw new AssertionError("installed signed preservation has 24");
      Pg387TrustedDeployment.SOURCE="32c6a7b1e79abf114901003c4a8f1300b33bf0c1";
      if(Pg387TrustedDeployment.expectedHistoryCount()!=26)throw new AssertionError("source replacement cannot borrow legacy count");
      Pg387TrustedDeployment.SOURCE="32c6a7b1e79abf114901003c4a8f1300b33bf0c0";
      Pg387TrustedDeployment.LABEL="PG421";
      if(Pg387TrustedDeployment.expectedHistoryCount()!=26)throw new AssertionError("new label cannot borrow legacy count");
      Pg387TrustedDeployment.SOURCE="a".repeat(40);
      if(Pg387TrustedDeployment.expectedHistoryCount()!=26)throw new AssertionError("approved new schema is 25 plus SCHEMA");
      System.out.println("PG421_SCHEMA_TOOL_PASS assertions=4 productionPtCount=0 legacyCountInferred=false");
    } finally {
      Pg387TrustedDeployment.LABEL=oldLabel;
      Pg387TrustedDeployment.SOURCE=oldSource;
    }
  }
}
