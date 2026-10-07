import dev.codex.schubert.nk.batch.file.RootBatchCredentialReader;
import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.client.impl.ServerLocatorImpl;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;
import org.apache.activemq.artemis.core.remoting.impl.netty.TransportConstants;

/** PG505 read-only Ops readiness diagnostic. No business queue send/consume, management
 * configuration, DB, attach, permit or Unit action. Private credential stays in Root memory.
 * NK-OPS-001/SS321342/SSC125; PT-OPS-PG506-006. Not parent admission evidence.
 */
public final class Pg510BrokerPressureReadonly {
  static String stage="ACTOR";
  static void actor()throws Exception{
    var value=new ChildStartupContext().verifyBroker(UUID.fromString("cc9ed874-7f4f-450e-a188-8de1e42c8441"),
        "0608718743a74668a5e5bd87cf30f6b5",new FixedServiceIdentity().resolveArtemis());
    if(value.pid()!=38602)throw new IllegalStateException("fixed actor changed");
  }
  public static void main(String[] args)throws Exception {
    if(args.length!=0 || !Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()
        .equals("cc9ed874-7f4f-450e-a188-8de1e42c8441"))throw new IllegalArgumentException("fixed diagnostic only");
    try {
      actor();stage="CREDENTIAL";
      try(var secret=dev.codex.schubert.nk.api.maintenance.InspectorDbCredential.consume(System.in.readNBytes(65537))){
        char[] password=secret.copyPassword();
        try(var locator=new ServerLocatorImpl(false,new TransportConfiguration(NettyConnectorFactory.class.getName(),
            Map.of("host","127.0.0.1","port",61616,TransportConstants.NETTY_CONNECT_TIMEOUT,5000)))){
          locator.setCallTimeout(5000).setCallFailoverTimeout(5000).setInitialConnectAttempts(1).setReconnectAttempts(0);
          stage="CONNECT";
          try(var factory=locator.createSessionFactory();
              var session=factory.createSession("schubert_ops",new String(password),false,true,true,false,0)){
            Arrays.fill(password,'\0');actor();session.start();stage="OPS_OBSERVATION";
            var values=new ArtemisStartupObservation().inspectEvidence(session);
            if(values.pressure().size()!=6)throw new IllegalStateException("fixed queue inventory mismatch");
            actor();
            long critical=values.pressure().values().stream().filter(value->value.state()==dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient.Pressure.CRITICAL).count();
            System.out.println("PG510_BROKER_PRESSURE queues6=true criticalCount="+critical+" readonly=true parentActions0=true");
          }
        }finally{Arrays.fill(password,'\0');}
      }
    }catch(Exception failure){
      System.err.println("PG510_BROKER_OPS verified=false stage="+stage+" type="+failure.getClass().getName()+" parentActions0=true");
      for(var frame:failure.getStackTrace())if(frame.getClassName().startsWith("dev.codex.schubert.nk.batch.mq.")
          || frame.getClassName().equals("Pg510BrokerPressureReadonly"))
        System.err.println("PG510_FRAME class="+frame.getClassName()+" method="+frame.getMethodName()+" line="+frame.getLineNumber());
      System.exit(2);
    }
  }
}
