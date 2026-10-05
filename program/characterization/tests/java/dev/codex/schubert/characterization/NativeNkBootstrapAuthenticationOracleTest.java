package dev.codex.schubert.characterization;
/** BOOT008 independent Python hashlib vector / SS314310000-iteration boundary, no native writes. */
public final class NativeNkBootstrapAuthenticationOracleTest {
  public static void main(String[] args)throws Exception{
    String vector="{pbkdf2-v1}000102030405060708090a0b0c0d0e0f36fecf295f40b075700c72b37adc19124bcdded8605e000ea5bfeb3a451fae70";
    NativeNkBootstrapAuthentication.independentPassword(vector,"QualityFixture467");int count=1;
    for(String encoded:new String[]{null,"",vector.substring(1),vector+"0",vector.toUpperCase(java.util.Locale.ROOT),vector.substring(0,vector.length()-1)+"1"}){
      try{NativeNkBootstrapAuthentication.independentPassword(encoded,"QualityFixture467");throw new AssertionError("invalid vector accepted");}catch(IllegalStateException expected){count++;}
    }
    for(String password:new String[]{null,"","WrongFixture467"}){
      try{NativeNkBootstrapAuthentication.independentPassword(vector,password);throw new AssertionError("wrong password accepted");}catch(IllegalStateException expected){count++;}
    }
    var json=new com.fasterxml.jackson.databind.ObjectMapper();
    var info=json.readTree("{\"commit\":\"literal-source\",\"app\":\"0.1.0-SNAPSHOT\",\"config\":\"1\",\"schema\":\"027\",\"protocol\":\"0.1.0-SNAPSHOT\"}");
    if(!NativeNkBootstrapAuthentication.information(info,"literal-source"))throw new AssertionError("fixed information rejected");count++;
    for(String text:new String[]{"null","[]","1","{}","{\"commit\":\"literal-source\"}"}){if(NativeNkBootstrapAuthentication.information(json.readTree(text),"literal-source"))throw new AssertionError("bad shape accepted");count++;}
    if(NativeNkBootstrapAuthentication.information(null,"literal-source") || NativeNkBootstrapAuthentication.information(info,null) || NativeNkBootstrapAuthentication.information(info,"foreign-source"))throw new AssertionError("null/foreign accepted");count+=3;
    for(String key:new String[]{"commit","app","config","schema","protocol"}){
      for(int mode=0;mode<4;mode++){
        var bad=(com.fasterxml.jackson.databind.node.ObjectNode)info.deepCopy();
        if(mode==0)bad.remove(key);else if(mode==1)bad.put(key,"foreign");else if(mode==2)bad.putNull(key);else bad.put(key,1);
        if(NativeNkBootstrapAuthentication.information(bad,"literal-source"))throw new AssertionError("bad field accepted");count++;
      }
    }
    var extra=(com.fasterxml.jackson.databind.node.ObjectNode)info.deepCopy();extra.put("unexpected","x");if(NativeNkBootstrapAuthentication.information(extra,"literal-source"))throw new AssertionError("unknown accepted");count++;
    System.out.println("NK_BOOTSTRAP_AUTH_ORACLE_PASS independentAssertions="+count+" productionPt0=true nativeMutation=false");
  }
}
