import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import java.nio.file.*;
import java.util.*;
import org.apache.activemq.artemis.utils.PasswordMaskingUtil;

/** SSC103/148 read-only isolated fixture observation; never prints secret values or hashes. */
public final class Pg410EffectiveBrokerAuth {
  static Properties read(Path path) throws Exception {
    byte[] raw=Files.readAllBytes(path);var p=new Properties();
    try(var in=new java.io.ByteArrayInputStream(raw)){p.load(in);}finally{Arrays.fill(raw,(byte)0);}
    return p;
  }
  static boolean matches(Properties users,String name,String service) throws Exception {
    String stored=users.getProperty(name);if(stored==null)return false;
    try(var credential=InspectorDbCredential.consume(Files.readAllBytes(Path.of("/etc/schubert-nk/credentials/mq-"+service)))) {
      char[] password=credential.copyPassword();
      try{return PasswordMaskingUtil.getHashProcessor(stored).compare(password,stored);}
      finally{Arrays.fill(password,'\0');}
    }
  }
  public static void main(String[] args) throws Exception {
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).strip().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated fixture only");
    var source=read(Path.of("/etc/schubert-nk/credentials/artemis-users"));
    var host=read(Path.of("/var/lib/schubert-nk/artemis/etc/artemis-users.properties"));
    var roles=read(Path.of("/var/lib/schubert-nk/artemis/etc/artemis-roles.properties"));
    for(String app:List.of("api","web")) {
      String old="schubert_"+app,next="nk_"+app;
      System.out.println("PG410_AUTH app="+app+" sourceOldCredentialMatches="+matches(source,old,app)
          +" sourceNewCredentialMatches="+matches(source,next,app)+" hostNewCredentialMatches="+matches(host,next,app)
          +" newRoleMatches="+next.equals(roles.getProperty(next)));
    }
    for(String name:List.of("ops","maintenance"))System.out.println("PG410_AUTH profile="+name+" originalCredentialMatches="+matches(source,"schubert_"+name,name));
    System.out.println("PG410_READ_ONLY vmMutation=false secretValuesOutput=false");
  }
}
