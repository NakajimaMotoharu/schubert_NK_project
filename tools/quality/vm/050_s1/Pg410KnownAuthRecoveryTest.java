import java.util.*;
public final class Pg410KnownAuthRecoveryTest {
  static int assertions;
  static void expect(boolean expected,Map<String,String> before,Map<String,String> after) {
    assertions++;if(Pg410KnownAuthRecovery.stoppedAfter(before,after)!=expected)throw new AssertionError("independent stopped relation");
  }
  public static void main(String[] args) {
    Pg410KnownAuthRecovery.configureVerifier();
    if(!Pg387TrustedDeployment.RELEASE.toString().equals("/opt/schubert-nk/releases/0.1.0-PG408")
        || !Pg387TrustedDeployment.LABEL.equals("PG408") || !Pg387TrustedDeployment.STEM.equals("pg408")
        || !Pg387TrustedDeployment.SOURCE.equals("32c6a7b1e79abf114901003c4a8f1300b33bf0c0"))throw new AssertionError("independent candidate four-value binding");
    assertions+=4;
    var approval=new dev.codex.schubert.nk.bootstrap.ReleaseApproval("0.1.0-PG408","33dda6beb4e17f7b6fc59a94f8a8dd4dfe29d904861fd338bf12c0de1ceec272");
    byte[] actual=("NKRELEASEAPPROVAL1\nversion=0.1.0-PG408\nmanifest_sha256=33dda6beb4e17f7b6fc59a94f8a8dd4dfe29d904861fd338bf12c0de1ceec272\n").getBytes(java.nio.charset.StandardCharsets.US_ASCII);
    if(!Pg410KnownAuthRecovery.sameApproval(approval,actual)
        || !Pg410KnownAuthRecovery.sameApproval(dev.codex.schubert.nk.bootstrap.ReleaseApproval.parse(actual),actual)
        || Pg410KnownAuthRecovery.sameApproval(approval,new String(actual,java.nio.charset.StandardCharsets.US_ASCII).replace("PG408","PG407").getBytes(java.nio.charset.StandardCharsets.US_ASCII))
        || Pg410KnownAuthRecovery.sameApproval(approval,new String(actual,java.nio.charset.StandardCharsets.US_ASCII).replace("33dd","44dd").getBytes(java.nio.charset.StandardCharsets.US_ASCII))
        || Pg410KnownAuthRecovery.sameApproval(approval,new byte[]{0}))throw new AssertionError("independent approval values");
    assertions+=5;
    var literal=new HashMap<String,String>();
    literal.put("Id","schubert-nk-api.service");literal.put("LoadState","loaded");
    literal.put("ActiveState","inactive");literal.put("SubState","dead");literal.put("Job","");
    literal.put("InvocationID","11111111111111111111111111111111");literal.put("Type","simple");
    literal.put("Restart","on-failure");literal.put("RemainAfterExit","no");literal.put("MainPID","0");literal.put("ControlPID","0");
    literal.put("Result","exit-code");literal.put("ExecMainStartTimestampMonotonic","100");literal.put("ExecMainExitTimestampMonotonic","200");
    literal.put("ExecMainCode","1");literal.put("ExecMainStatus","1");literal.put("KillMode","control-group");literal.put("SendSIGKILL","no");
    expect(true,literal,literal);expect(false,null,literal);expect(false,literal,null);
    for(String field:literal.keySet()) {
      var bad=new HashMap<>(literal);bad.put(field,null);expect(false,literal,bad);expect(false,bad,literal);
      bad=new HashMap<>(literal);bad.remove(field);expect(false,literal,bad);
    }
    for(String field:List.of("Id","LoadState","Job","InvocationID","Type","Restart","RemainAfterExit","MainPID","ControlPID",
        "ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic","ExecMainCode","ExecMainStatus","KillMode","SendSIGKILL")) {
      var bad=new HashMap<>(literal);bad.put(field,"different");expect(false,literal,bad);
    }
    var failed=new HashMap<>(literal);failed.put("ActiveState","failed");failed.put("SubState","failed");expect(true,literal,failed);
    var cold=new HashMap<>(literal);cold.put("InvocationID","");cold.put("Result","success");
    for(String field:List.of("ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic"))cold.put(field,"0");
    expect(true,literal,cold);
    for(String field:List.of("InvocationID","ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic","Result")) {
      var partial=new HashMap<>(cold);partial.put(field,literal.get(field));expect(false,literal,partial);
    }
    var wrong=new HashMap<>(literal);wrong.put("Result","timeout");expect(false,literal,wrong);
    wrong=new HashMap<>(literal);wrong.put("ActiveState","active");wrong.put("SubState","running");expect(false,literal,wrong);
    wrong=new HashMap<>(literal);wrong.put("extra","value");expect(false,literal,wrong);
    System.out.println("PG410_TOOL_LOGIC independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
