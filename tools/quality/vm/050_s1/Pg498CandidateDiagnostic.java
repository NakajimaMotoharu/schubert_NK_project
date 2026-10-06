import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.ReleaseApproval;
/** BUG807: standalone candidate readonly diagnostic; no M/A acquisition or deployment. */
public final class Pg498CandidateDiagnostic {
  public static void main(String[] args)throws Exception{
    try{
      var approval=new ReleaseApproval("0.1.0-PG495","f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44");
      StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verifyCandidate(approval);
      System.out.println("PG498_CANDIDATE_DIAGNOSTIC actual0=true changes0=true");
    }catch(Exception failure){
      for(Throwable current=failure;current!=null;current=current.getCause()){
        System.out.println("PG498_TYPE "+current.getClass().getName());
        for(var frame:current.getStackTrace())System.out.println("PG498_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
      }
      throw new IllegalStateException("candidate readonly rejected");
    }
  }
}
