import java.util.*;
public final class Pg468BootstrapCredentialRetirementTest{
  public static void main(String[] args){int checks=0;var valid=Map.<String,Object>of("uid",0,"gid",0,"mode",0100400,"nlink",1,"size",43L);if(!Pg468BootstrapCredentialRetirement.metadata(valid))throw new AssertionError("literal0400 rejected");checks++;
    if(Pg468BootstrapCredentialRetirement.metadata(null))throw new AssertionError("null accepted");checks++;
    for(String key:valid.keySet())for(Object value:new Object[]{null,"unknown",-1,0L}){var bad=new HashMap<>(valid);bad.put(key,value);if(Pg468BootstrapCredentialRetirement.metadata(bad))throw new AssertionError("invalid accepted");checks++;}
    for(long size:new long[]{1,128}){var edge=new HashMap<>(valid);edge.put("size",size);if(!Pg468BootstrapCredentialRetirement.metadata(edge))throw new AssertionError("valid bound rejected");checks++;}
    for(long size:new long[]{0,129,Long.MAX_VALUE}){var edge=new HashMap<>(valid);edge.put("size",size);if(Pg468BootstrapCredentialRetirement.metadata(edge))throw new AssertionError("invalid bound accepted");checks++;}
    if(!Pg468BootstrapCredentialRetirement.SOURCES.equals(Set.of("bootstrap-admin-username","bootstrap-admin-password")))throw new AssertionError("retirement set differs");checks++;
    System.out.println("PG468_BOOTSTRAP_RETIREMENT_ORACLE independentAssertions="+checks+" nativeMutation=false productionPT0=true");
  }
}
