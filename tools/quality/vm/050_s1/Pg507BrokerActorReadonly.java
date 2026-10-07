import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

/** PG505 unresolved broker projection diagnostic. Passive public identity reads only.
 * No attach, signals, JMS connection, DB connection, permit, start/stop or native mutation.
 * NK-OPS-001/SS342/SSC125; PT-OPS-PG506-005; retained parent ownership is not borrowed.
 */
public final class Pg507BrokerActorReadonly {
  public static void main(String[] args)throws Exception {
    if(args.length!=0 || !Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()
        .equals("cc9ed874-7f4f-450e-a188-8de1e42c8441"))throw new IllegalArgumentException("fixed diagnostic only");
    try {
      var actor=new ChildStartupContext().verifyBroker(UUID.fromString("cc9ed874-7f4f-450e-a188-8de1e42c8441"),
          "0608718743a74668a5e5bd87cf30f6b5",new FixedServiceIdentity().resolveArtemis());
      if(actor.pid()!=38602)throw new IllegalStateException("fixed broker generation changed");
      System.out.println("PG507_BROKER_ACTOR verified=true readsOnly=true parentOrBrokerActions0=true");
    }catch(Exception failure){
      System.err.println("PG507_BROKER_ACTOR verified=false type="+failure.getClass().getName()+" readsOnly=true");
      for(var frame:failure.getStackTrace())if(frame.getClassName().startsWith("dev.codex.schubert.nk.bootstrap."))
        System.err.println("PG507_FRAME class="+frame.getClassName()+" method="+frame.getMethodName()+" line="+frame.getLineNumber());
      System.exit(2);
    }
  }
}
