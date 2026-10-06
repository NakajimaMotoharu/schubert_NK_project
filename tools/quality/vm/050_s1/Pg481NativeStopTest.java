import java.util.*;

/** Literal fixed eight-unit order/fail-fast and unknown-retention oracle. */
public final class Pg481NativeStopTest {
  static int checks;
  static void check(boolean value){checks++;if(!value)throw new AssertionError("native stop vector "+checks);}
  public static void main(String[] args)throws Exception{
    Pg464CodeOnlyDeployment.configure("PG479","bab704707b8fd7e0dc7581c4489f0892236efe73",java.nio.file.Path.of("/opt/schubert-nk/releases/0.1.0-PG479"));
    check(Pg387TrustedDeployment.STEM.equals("pg479"));check(Pg387TrustedDeployment.LABEL.equals("PG479"));
    check(Pg387TrustedDeployment.SOURCE.equals("bab704707b8fd7e0dc7581c4489f0892236efe73"));
    check(Pg387TrustedDeployment.RELEASE.equals(java.nio.file.Path.of("/opt/schubert-nk/releases/0.1.0-PG479")));
    var order=List.of("caddy.service","schubert-nk-web.service","schubert-nk-api.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service","artemis.service");
    var calls=new ArrayList<String>();Pg471CompletedDeployment.stopOwned(calls::add);check(calls.equals(order));
    for(int at=0;at<order.size();at++){
      var observed=new ArrayList<String>();final int point=at;var failure=new java.io.IOException("literal stop failure");
      try{Pg471CompletedDeployment.stopOwned(unit->{observed.add(unit);if(observed.size()==point+1)throw failure;});throw new AssertionError("fault not reached");}
      catch(java.io.IOException actual){check(actual==failure);check(observed.equals(order.subList(0,at+1)));}
    }
    var body=new java.io.IOException("literal body");
    check(!Pg481NativeStop.retainRequired("BODY",false,body));
    check(Pg481NativeStop.retainRequired("BODY",true,body));
    for(String phase:List.of("DATABASE_SCOPE_CLOSE","A_SCOPE_CLOSE","M_SCOPE_CLOSE"))check(Pg481NativeStop.retainRequired(phase,false,body));
    check(Pg481NativeStop.retainRequired("BODY",false,new AssertionError("fatal")));
    body.addSuppressed(new java.io.IOException("secondary"));check(Pg481NativeStop.retainRequired("BODY",false,body));
    System.out.println("PG481_NATIVE_STOP_TEST independentAssertions="+checks+" processActions0=true productionPT0=true");
  }
}
