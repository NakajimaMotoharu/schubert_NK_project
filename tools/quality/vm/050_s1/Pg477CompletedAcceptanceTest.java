import java.nio.charset.StandardCharsets;
/** Independent literal argument/transport oracle; no VM authority. */
public final class Pg477CompletedAcceptanceTest {
  private static int checks;
  private static void check(boolean value){checks++;if(!value)throw new AssertionError("completed boundary oracle");}
  public static void main(String[] args){
    check(Pg477CompletedAcceptance.arguments(new String[]{"verify"}));
    for(String[] wrong:new String[][]{null,{}, {null},{"activate"},{"verify","extra"},{"VERIFY"}})check(!Pg477CompletedAcceptance.arguments(wrong));
    for(String expected:new String[]{"REF_READY","REF_CHECKED","REF_RELEASED"}){
      byte[] literal=(expected+"\n").getBytes(StandardCharsets.US_ASCII);
      check(Pg477CompletedReferences.reply(expected,literal));
      for(byte[] wrong:new byte[][]{null,{},expected.getBytes(StandardCharsets.US_ASCII),(expected+"\r\n").getBytes(StandardCharsets.US_ASCII),new byte[65],"REF_FAILED\n".getBytes(StandardCharsets.US_ASCII)})check(!Pg477CompletedReferences.reply(expected,wrong));
    }
    check(!Pg477CompletedReferences.reply(null,new byte[0]));check(!Pg477CompletedReferences.reply("foreign",new byte[0]));
    System.out.println("PG477_COMPLETED_TEST independentAssertions="+checks+" productionPT0=true nativeMutation0=true");
  }
}
